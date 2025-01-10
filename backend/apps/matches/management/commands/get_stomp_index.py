from django.core.management import BaseCommand
from matplotlib import pyplot as plt

from apps.matches.models import SimpleMatch
import math

"""
Regresja nie do końca działa przy ograniczonych wartościach.
Znormalizować wspołczynniki do 0 - 1, a potem rozciągnać odwróconą funkcją logistyczną, 0 to - inf 1 to + inf

"""


def flatten(x):
    return round(abs(math.tanh(x / 2)) / 2, 4)


def calculate_index(game, gold, kill, exp, won):
    sm_filter = SimpleMatch.objects.filter(game_duration__lt=3600).filter(game_duration__gte=200)
    max_game = sm_filter.order_by("-game_duration").first().game_duration
    max_gold = sm_filter.order_by("-gold_difference").first().gold_difference
    max_kill = sm_filter.order_by("-kill_difference").first().kill_difference
    max_exp = sm_filter.order_by("-exp_difference").first().exp_difference
    # print(max_game, max_gold, max_kill, max_exp)
    x1 = 1 - (game / max_game)
    x2 = 2 * abs(gold / max_gold)
    x3 = abs(kill / max_kill) / 2
    x4 = abs(exp / max_exp)
    x = x1 + x2 + x3 + x4
    flat = flatten(x)
    if won:
        y = 0.5 + flat
    else:
        y = 0.5 - flat
    # print(x1)
    # print(x2)
    # print(x3)
    # print(x4)
    # print(f"Flat: {flat}")
    return round(y, 4)


class Command(BaseCommand):

    def handle(self, *args, **options):
        # print(SimpleMatch.objects.filter(game_duration__gte=3600).count())
        # print(SimpleMatch.objects.filter(won=True).count())
        # print(SimpleMatch.objects.filter(won=False).count())
        x = 50
        matches = SimpleMatch.objects.values()[x:x+1]
        #
        # print("---------")
        for match in matches:
            print(match)
            print(calculate_index(match["game_duration"], match["gold_difference"], match["kill_difference"],
                                  match["exp_difference"], match["won"]))
        # matches = SimpleMatch.objects.filter(game_duration__lt=3600).filter(game_duration__gte=200).values_list(
        #     "gold_difference", flat=True)

        # with open("stomp.csv", 'w', newline='') as csvfile:
        #     for match in matches:
        #         csvfile.write(f"{unpack(match)}\n")
        # print(matches)
        # plt.hist(matches, bins=50)
        # plt.savefig("plots")
        # plt.clf()
        # plt.boxplot(matches)
        # plt.savefig("box")
