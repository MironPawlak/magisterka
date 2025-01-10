from django.core.management import BaseCommand

from apps.matches.models import Champion, MatchChampion


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("champion", nargs=1, type=str)

    def handle(self, *args, **options):
        name = options["champion"][0]
        print(name)
        champion = Champion.objects.get(name=name)

        enemies = Champion.objects.filter(position=champion.position).exclude(id=champion.id)
        stat_dict = {}
        blue_won = set(MatchChampion.objects.filter(champion=champion, team_id=100, win=True).values_list("match_id",
                                                                                                          flat=True))
        red_won = set(MatchChampion.objects.filter(champion=champion, team_id=200, win=True).values_list("match_id",
                                                                                                         flat=True))
        blue_lost = set(MatchChampion.objects.filter(champion=champion, team_id=100, win=False).values_list("match_id",
                                                                                                            flat=True))
        red_lost = set(MatchChampion.objects.filter(champion=champion, team_id=200, win=False).values_list("match_id",
                                                                                                           flat=True))

        for champ in enemies:
            blue_enemy = MatchChampion.objects.filter(champion=champ, team_id=200).values_list("match_id",
                                                                                               flat=True)
            red_enemy = MatchChampion.objects.filter(champion=champ, team_id=100).values_list("match_id", flat=True)

            wins = len(blue_won & set(blue_enemy)) + len(red_won & set(red_enemy))
            losses = len(blue_lost & set(blue_enemy)) + len(red_lost & set(red_enemy))
            stat_dict[champ.name] = {"wins": losses, "losses": wins, "ratio": f"{(losses / (wins + losses + 1) * 100):.2f}"}

        print(sorted(stat_dict.items(), key=lambda x: x[1]["ratio"], reverse=True))
