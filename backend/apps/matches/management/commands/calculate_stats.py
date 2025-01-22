import datetime

from django.core.management import BaseCommand

from apps.matches.models import Champion, Statistic, MatchChampion


class Command(BaseCommand):

    def handle(self, *args, **options):
        Statistic.objects.all().delete()
        champions = Champion.objects.all()
        for champion in champions:
            win = MatchChampion.objects.filter(champion=champion).filter(
                match__date__gt=datetime.date(2025, 1, 8)).filter(win=True).count()
            lose = MatchChampion.objects.filter(champion=champion).filter(
                match__date__gt=datetime.date(2025, 1, 8)).filter(win=False).count()
            bans = champion.bans.count()
            Statistic.objects.create(champion=champion, wins=win, losses=lose, bans=bans)
