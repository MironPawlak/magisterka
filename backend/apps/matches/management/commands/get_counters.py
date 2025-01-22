import datetime

from django.core.management import BaseCommand

from apps.matches.models import Champion, MatchChampion, SimpleMatch, ChampionCounters
from apps.matches.serializers import CounterOutputSerializer


class Command(BaseCommand):

    def handle(self, *args, **options):
        ChampionCounters.objects.all().delete()
        for champion in Champion.objects.all():
            filter_date = datetime.date(2025, 1, 8)
            enemies = Champion.objects.filter(position=champion.position).exclude(id=champion.id)
            blue = MatchChampion.objects.filter(champion=champion, team_id=100).filter(
                match__date__gt=filter_date).values_list("id", flat=True)
            red = MatchChampion.objects.filter(champion=champion, team_id=200).filter(
                match__date__gt=filter_date).values_list("id", flat=True)
            stat_list = []
            for enemy in enemies:
                enemy_blue = MatchChampion.objects.filter(champion=enemy, team_id=100).filter(
                    match__date__gt=filter_date).values_list("id", flat=True)
                enemy_red = MatchChampion.objects.filter(champion=enemy, team_id=200).filter(
                    match__date__gt=filter_date).values_list("id", flat=True)
                blue_won = SimpleMatch.objects.filter(matchchampion__id__in=red).filter(
                    matchchampion__id__in=enemy_blue).filter(date__gt=filter_date).filter(won=True).count()
                red_won = SimpleMatch.objects.filter(matchchampion__id__in=blue).filter(
                    matchchampion__id__in=enemy_red).filter(date__gt=filter_date).filter(won=False).count()
                blue_lost = SimpleMatch.objects.filter(matchchampion__id__in=red).filter(
                    matchchampion__id__in=enemy_blue).filter(date__gt=filter_date).filter(won=False).count()
                red_lost = SimpleMatch.objects.filter(matchchampion__id__in=blue).filter(
                    matchchampion__id__in=enemy_red).filter(date__gt=filter_date).filter(won=True).count()
                won = blue_won + red_won
                lost = blue_lost + red_lost
                stat_list.append(
                    {'champion': enemy, "wins": won, "losses": lost,
                     "ratio": f"{(won / (won + lost + 1) * 100):.2f}"}
                )
            data = sorted(stat_list, key=lambda x: x["ratio"], reverse=True)
            ChampionCounters.objects.create(champion=champion, counters=CounterOutputSerializer(data, many=True).data)
