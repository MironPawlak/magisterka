from django.core.management import BaseCommand

from apps.matches.models import SimpleMatch, Match


class Command(BaseCommand):

    def handle(self, *args, **options):

        matches = SimpleMatch.objects.order_by("id")
        for match in matches:
            m = Match.objects.filter(riot_id=match.riot_id).first()
            data = m.data
            game_duration = data["info"]["gameDuration"]
            gold_difference = 0
            exp_difference = 0
            kill_difference = 0
            win = next((x["win"] for x in data["info"]["participants"] if x["teamId"] == 100), None)
            for player in data["info"]["participants"]:
                if player["teamId"] == 100:
                    # win = True if player["win"] else False
                    gold_difference += player["goldEarned"]
                    exp_difference += player["champExperience"]
                    kill_difference += player["kills"]
                else:
                    gold_difference -= player["goldEarned"]
                    exp_difference -= player["champExperience"]
                    kill_difference -= player["kills"]
            # print(match.riot_id, game_duration, gold_difference, exp_difference, kill_difference, win)
            match.kill_difference = kill_difference
            match.game_duration = game_duration
            match.gold_difference = gold_difference
            match.exp_difference = exp_difference
            match.won = win
            match.save()
