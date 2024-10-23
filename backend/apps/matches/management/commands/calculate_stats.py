import sys

from django.core.management import BaseCommand

from apps.matches.models import Match, Champion, Statistic


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Old code
        # champions = Champion.objects.all()
        # for champion in champions:
        #     wins = Match.objects.filter(
        #         data__info__participants__contains=[{"win": True, "championId": champion.key}]).count()
        #     losses = Match.objects.filter(
        #         data__info__participants__contains=[{"win": False, "championId": champion.key}]).count()
        #     bans = Match.objects.filter(data__info__teams__0__bans__contains=[{"championId": champion.key}]).count()
        #     if Statistic.objects.filter(champion=champion).exists():
        #         Statistic.objects.filter(champion=champion).update(wins=wins, losses=losses, bans=bans)
        #     else:
        #         Statistic.objects.create(champion=champion, wins=wins, losses=losses, bans=bans)
        stats = {}
        for champion in Champion.objects.order_by("key").all():
            stats.setdefault(champion.key, {"won": 0, "lost": 0, "bans": 0})

        for match in Match.objects.filter(data__isnull=False).order_by("id").all():
            sys.stdout.write("\rMatch id %i " % match.id)
            sys.stdout.flush()
            for team in match.data["info"]["teams"]:
                for ban in team["bans"]:
                    if ban["championId"] != -1:
                        stats[ban["championId"]]["bans"] += 1
            for participant in match.data["info"]["participants"]:
                if participant["win"]:
                    stats[participant["championId"]]["won"] += 1
                else:
                    stats[participant["championId"]]["lost"] += 1

        Statistic.objects.all().delete()
        for key, value in stats.items():
            champion = Champion.objects.get(key=key)
            Statistic.objects.create(champion=champion, wins=value["won"], losses=value["lost"], bans=value["bans"])

