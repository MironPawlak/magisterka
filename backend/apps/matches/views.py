import datetime
import keras

import pandas as pd
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from rest_framework import views, status
from rest_framework.response import Response

from apps.matches.management.commands.create_csv import translate_champions
from apps.matches.models import Statistic, Champion, ChampionCounters
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
        try:
            loaded_model = keras.saving.load_model("data/model.keras")
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
            prediction = loaded_model.predict(champions)
            prediction_list.append({"champion": champion, "predicted": prediction[0]})

        prediction_list = sorted(prediction_list, key=lambda x: x["predicted"], reverse=True)[:3]

        champions = pd.DataFrame([translate_champions(allies_list, enemies_list, "riot_id")])
        prediction = loaded_model.predict(champions)

        data = {"current_prediction": prediction[0],
                "top_predictions": prediction_list}

        return Response(status=status.HTTP_200_OK, data=PredictionOutputSerializer(data).data)


class GetCountersView(views.APIView):

    def get(self, request, *args, **kwargs):
        filter_date = datetime.date(2025, 1, 8)
        champion = Champion.objects.filter(name__icontains=self.kwargs["name"]).first()
        if champion is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        counters = ChampionCounters.objects.get(champion=champion).counters
        return Response(status=status.HTTP_200_OK, data=CounterOutputSerializer(counters, many=True).data)


class GetStatistics(views.APIView):

    def get(self, request, *args, **kwargs):
        serializer = StatSerializer(data={'position': self.kwargs["position"]})
        serializer.is_valid(raise_exception=True)
        stats = Statistic.objects.filter(champion__position=serializer.validated_data["position"]).annotate(
            ratio=Cast(F("wins"), FloatField()) / (F("wins") + F("losses"))).order_by("-ratio")

        return Response(status=status.HTTP_200_OK, data=StatisticSerializer(stats, many=True).data)
