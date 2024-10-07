from django.core.management import BaseCommand

from apps.matches.models import Match, Champion, Statistic


class Command(BaseCommand):

    def handle(self, *args, **options):
        champions = Champion.objects.all()
        for champion in champions:
            wins = Match.objects.filter(
                data__info__participants__contains=[{"win": True, "championId": champion.key}]).count()
            losses = Match.objects.filter(
                data__info__participants__contains=[{"win": False, "championId": champion.key}]).count()
            bans = Match.objects.filter(data__info__teams__0__bans__contains=[{"championId": champion.key}]).count()
            if Statistic.objects.filter(champion=champion).exists():
                Statistic.objects.filter(champion=champion).update(wins=wins, losses=losses, bans=bans)
            else:
                Statistic.objects.create(champion=champion, wins=wins, losses=losses, bans=bans)
