import datetime

from django.core.management import BaseCommand

from apps.matches.management.commands.get_stomp_index import calculate_index
from apps.matches.models import SimpleMatch, Champion, ChampionClass


def unpack(s, neg=False):
    if neg:
        return ",".join(map(str, [-x for x in s]))
    else:
        return ",".join(map(str, s))


def translate_champions(blue, red, attribute):
    champ_list = []
    # inv_champ_list = []
    for champ in Champion.objects.all():
        if getattr(champ, attribute) in blue:
            champ_list.append(1)
            # inv_champ_list.append(-1)
        elif getattr(champ, attribute) in red:
            champ_list.append(-1)
            # inv_champ_list.append(1)
        else:
            champ_list.append(0)
            # inv_champ_list.append(0)

    return champ_list


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv_name = "data/matches.csv"
        sm = SimpleMatch.objects.filter(date__gt=datetime.date(2024, 11, 1)).iterator()
        model_fields = [f"champion__champ_class__{field.name}" for field in ChampionClass._meta.get_fields() if
                        field.name in ("true_dmg_taken", "magic_dmg_taken", "physical_dmg_taken", "self_dmg_mitigated",
                                       "true_dmg_dealt", "magic_dmg_dealt", "physical_dmg_dealt")]
        # model_fields = ["champion__name"]
        with open(csv_name, 'w', newline='') as csvfile:
            for match in sm:
                if match.matchchampion_set.filter(team_id=100).first().win:
                    winner = 1
                else:
                    winner = 0
                # winner = calculate_index(match.game_duration, match.gold_difference, match.kill_difference,
                #                        match.exp_difference, match.won)

                if csv_name == "data/matches.csv":
                    blue = set(match.matchchampion_set.filter(team_id=100).values_list("champion_id", flat=True))
                    red = set(match.matchchampion_set.filter(team_id=200).values_list("champion_id", flat=True))
                    champ_list = translate_champions(blue, red, "id")
                    # inv_champ_list = []

                    csvfile.write(f"{unpack(champ_list)},{winner}\n")

                elif csv_name == "data/matches_class.csv":
                    blue = match.matchchampion_set.filter(team_id=100).order_by("champion__position").values_list(
                        *model_fields)
                    red = match.matchchampion_set.filter(team_id=200).order_by("champion__position").values_list(
                        *model_fields)
                    blue_str = ""
                    red_str = ""

                    for champ in blue:
                        blue_str += unpack(champ) + ','
                    for champ in red:
                        red_str += unpack(champ) + ','
                    csvfile.write(f"{blue_str[:-1]},{red_str[:-1]},{winner}\n")

