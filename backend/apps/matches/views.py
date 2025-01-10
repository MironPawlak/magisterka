import pickle

import pandas as pd
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from rest_framework import views, status
from rest_framework.response import Response

from apps.matches.management.commands.create_csv import translate_champions
from apps.matches.models import Statistic, Champion, SimpleMatch, MatchChampion
from apps.matches.serializers import PredictionInputSerializer, StatSerializer, StatisticSerializer, \
    PredictionOutputSerializer, CounterOutputSerializer


# Create your views here.

class GetPredictionView(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = PredictionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        allies = Champion.objects.filter(key__in=vd["allies"])
        enemies = Champion.objects.filter(key__in=vd["enemies"])
        bans = Champion.objects.filter(key__in=vd["bans"])
        try:
            with open('data/model.pkl', 'rb') as f:
                loaded_model = pickle.load(f)
        except FileNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        champions = Champion.objects.exclude(key__in=vd["allies"]).exclude(key__in=vd["enemies"]).exclude(
            key__in=vd["bans"]).filter(position=vd["position"])

        prediction_list = []
        allies_list = list(allies.values_list("riot_id", flat=True))
        enemies_list = list(enemies.values_list("riot_id", flat=True))

        for champion in champions:
            joined_allies = allies_list + [champion.riot_id]
            champions = pd.DataFrame([translate_champions(joined_allies, enemies_list, "riot_id")])
            prediction = loaded_model.predict_proba(champions)
            prediction_list.append({"champion": champion, "predicted": prediction[0][1]})

        prediction_list = sorted(prediction_list, key=lambda x: x["predicted"], reverse=True)[:3]

        champions = pd.DataFrame([translate_champions(allies_list, enemies_list, "riot_id")])
        prediction = loaded_model.predict_proba(champions)

        data = {"current_prediction": prediction[0][1],
                "top_predictions": prediction_list}

        return Response(status=status.HTTP_200_OK, data=PredictionOutputSerializer(data).data)


class GetCountersView(views.APIView):

    def get(self, request, *args, **kwargs):
        champion = Champion.objects.filter(name__icontains=self.kwargs["name"]).first()
        if champion is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        enemies = Champion.objects.filter(position=champion.position).exclude(id=champion.id)
        blue = MatchChampion.objects.filter(champion=champion, team_id=100).values_list("id", flat=True)
        red = MatchChampion.objects.filter(champion=champion, team_id=200).values_list("id", flat=True)
        stat_list = []
        for enemy in enemies:
            enemy_blue = MatchChampion.objects.filter(champion=enemy, team_id=100).values_list("id", flat=True)
            enemy_red = MatchChampion.objects.filter(champion=enemy, team_id=200).values_list("id", flat=True)

            blue_won = SimpleMatch.objects.filter(matchchampion__id__in=red).filter(
                matchchampion__id__in=enemy_blue).filter(
                won=True).count()
            red_won = SimpleMatch.objects.filter(matchchampion__id__in=blue).filter(
                matchchampion__id__in=enemy_red).filter(
                won=False).count()
            blue_lost = SimpleMatch.objects.filter(matchchampion__id__in=red).filter(
                matchchampion__id__in=enemy_blue).filter(
                won=False).count()
            red_lost = SimpleMatch.objects.filter(matchchampion__id__in=blue).filter(
                matchchampion__id__in=enemy_red).filter(
                won=True).count()
            won = blue_won + red_won
            lost = blue_lost + red_lost
            stat_list.append(
                {'champion': enemy, "wins": won, "losses": lost,
                 "ratio": f"{(won / (won + lost + 1) * 100):.2f}"}
            )
        data = sorted(stat_list, key=lambda x: x["ratio"], reverse=True)
        return Response(status=status.HTTP_200_OK, data=CounterOutputSerializer(data, many=True).data)


class GetStatistics(views.APIView):

    def get(self, request, *args, **kwargs):
        serializer = StatSerializer(data={'position': self.kwargs["position"]})
        serializer.is_valid(raise_exception=True)
        stats = Statistic.objects.filter(champion__position=serializer.validated_data["position"]).annotate(
            ratio=Cast(F("wins"), FloatField()) / (F("wins") + F("losses"))).order_by("-ratio")

        return Response(status=status.HTTP_200_OK, data=StatisticSerializer(stats, many=True).data)
