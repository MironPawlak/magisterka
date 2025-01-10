from datetime import datetime

from django.core.management import BaseCommand
from apps.matches.models import SimpleMatch, Match, MatchChampion, Champion


class Command(BaseCommand):

    def handle(self, *args, **options):

        # loaded_matches = SimpleMatch.objects.values_list("riot_id", flat=True).order_by("id")
        # matches = Match.objects.exclude(riot_id__in=loaded_matches).exclude(data__isnull=True)
        matches = Match.objects.exclude(data__isnull=True).iterator()
        for match in matches:
            if SimpleMatch.objects.filter(riot_id=match.riot_id).exists():
                continue
            game_duration = match.data["info"]["gameDuration"]
            gold_difference = 0
            exp_difference = 0
            kill_difference = 0
            win = next((x["win"] for x in match.data["info"]["participants"] if x["teamId"] == 100), None)
            for player in match.data["info"]["participants"]:
                if player["teamId"] == 100:
                    gold_difference += player["goldEarned"]
                    exp_difference += player["champExperience"]
                    kill_difference += player["kills"]
                else:
                    gold_difference -= player["goldEarned"]
                    exp_difference -= player["champExperience"]
                    kill_difference -= player["kills"]

            timestamp = match.data["info"]["gameCreation"] / 1000
            sm = SimpleMatch.objects.create(riot_id=match.riot_id, date=datetime.fromtimestamp(timestamp),
                                            kill_difference=kill_difference, game_duration=game_duration,
                                            gold_difference=gold_difference, exp_difference=exp_difference, won=win)

            for pick in match.data["info"]["participants"]:
                champion = Champion.objects.get(key=pick["championId"])
                MatchChampion.objects.create(match=sm, champion=champion, win=pick["win"], team_id=pick["teamId"])
            for team in match.data["info"]["teams"]:
                for ban in team["bans"]:
                    if ban["championId"] != -1:
                        champion = Champion.objects.get(key=ban["championId"])
                        # TODO if both teams ban same champion it counts as one ban
                        sm.bans.add(champion)
