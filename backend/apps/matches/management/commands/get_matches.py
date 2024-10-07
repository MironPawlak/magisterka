import time
from datetime import datetime

from django.core.management import BaseCommand
from django.conf import settings
from riotwatcher import LolWatcher
from apps.matches.models import Match, Player
from django.core.management import CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):

        lol_watcher = LolWatcher(settings.RIOT_KEY)
        region = 'EUN1'

        while True:
            matches = Match.objects.filter(data__isnull=True).order_by("id")
            for match in matches:
                response = lol_watcher.match.by_id(region=region, match_id=match.riot_id)
                match.data = response
                match.save()
                participants = match.data["metadata"]["participants"]
                for participant in participants:
                    if not Player.objects.filter(puuid=participant).exists():
                        Player.objects.create(puuid=participant)

            if player := Player.objects.order_by("last_update").first():
                match_list = lol_watcher.match.matchlist_by_puuid(puuid=player.puuid, queue=420, region=region,
                                                                  start_time=int(player.last_update.timestamp()),
                                                                  count=100)
                for match in match_list:
                    if not Match.objects.filter(riot_id=match).exists():
                        Match.objects.create(riot_id=match)
                player.last_update = datetime.now()
                player.save()

            time.sleep(1)
            print('Pause')
            if not matches and not player:
                raise CommandError("End of data")
