from django.core.management import BaseCommand
import json
from apps.matches.models import Match, ChampionClass, Champion
from apps.matches.utils import batch_qs


class Command(BaseCommand):

    def handle(self, *args, **options):

        data = {}
        matches = Match.objects.exclude()
        for start, end, total, qs in batch_qs(matches, 1000):
            for match in qs:
                for pick in match.data["info"]["participants"]:
                    champ_id = pick["championId"]
                    if champ_id not in data:
                        data[champ_id] = {
                            "games_played": 0,
                            "gold_earned": 0,
                            "experience": 0,
                            "kills": 0,
                            "deaths": 0,
                            "assists": 0,
                            "time_ccing": 0,
                            "total_cc_time": 0,
                            "turret_takedowns": 0,
                            "true_dmg_taken": 0,
                            "magic_dmg_taken": 0,
                            "physical_dmg_taken": 0,
                            "self_dmg_mitigated": 0,
                            "true_dmg_dealt": 0,
                            "magic_dmg_dealt": 0,
                            "physical_dmg_dealt": 0,
                            "minions_killed": 0,
                            "turrets_dmg_dealt": 0,
                            "teammate_heals": 0,
                            "teammate_shields": 0,
                            "self_heal": 0,  # Total - teammate
                        }

                    data[champ_id]["games_played"] += 1
                    data[champ_id]["gold_earned"] += pick["goldEarned"]
                    data[champ_id]["experience"] += pick["champExperience"]
                    data[champ_id]["kills"] += pick["kills"]
                    data[champ_id]["deaths"] += pick["deaths"]
                    data[champ_id]["assists"] += pick["assists"]
                    data[champ_id]["time_ccing"] += pick["timeCCingOthers"]
                    data[champ_id]["total_cc_time"] += pick["totalTimeCCDealt"]
                    data[champ_id]["turret_takedowns"] += pick["turretTakedowns"]
                    data[champ_id]["true_dmg_taken"] += pick["trueDamageTaken"]
                    data[champ_id]["magic_dmg_taken"] += pick["magicDamageTaken"]
                    data[champ_id]["physical_dmg_taken"] += pick["physicalDamageTaken"]
                    data[champ_id]["self_dmg_mitigated"] += pick["damageSelfMitigated"]
                    data[champ_id]["true_dmg_dealt"] += pick["trueDamageDealtToChampions"]
                    data[champ_id]["magic_dmg_dealt"] += pick["magicDamageDealtToChampions"]
                    data[champ_id]["physical_dmg_dealt"] += pick["physicalDamageDealtToChampions"]
                    data[champ_id]["turrets_dmg_dealt"] += pick["damageDealtToTurrets"]
                    data[champ_id]["teammate_heals"] += pick["totalHealsOnTeammates"]
                    data[champ_id]["teammate_shields"] += pick["totalDamageShieldedOnTeammates"]
                    data[champ_id]["self_heal"] += (pick["totalHeal"] - pick["totalHealsOnTeammates"])

        print(json.dumps(data, indent=2))
        ChampionClass.objects.all().delete()

        for key, value in data.items():
            c = Champion.objects.get(key=key)
            ChampionClass.objects.create(
                champion=c,
                gold_earned=value["gold_earned"] / value["games_played"],
                experience=value["experience"] / value["games_played"],
                kills=value["kills"] / value["games_played"],
                deaths=value["deaths"] / value["games_played"],
                assists=value["assists"] / value["games_played"],
                time_ccing=value["time_ccing"] / value["games_played"],
                total_cc_time=value["total_cc_time"] / value["games_played"],
                turret_takedowns=value["turret_takedowns"] / value["games_played"],
                true_dmg_taken=value["true_dmg_taken"] / value["games_played"],
                magic_dmg_taken=value["magic_dmg_taken"] / value["games_played"],
                physical_dmg_taken=value["physical_dmg_taken"] / value["games_played"],
                self_dmg_mitigated=value["self_dmg_mitigated"] / value["games_played"],
                true_dmg_dealt=value["true_dmg_dealt"] / value["games_played"],
                magic_dmg_dealt=value["magic_dmg_dealt"] / value["games_played"],
                physical_dmg_dealt=value["physical_dmg_dealt"] / value["games_played"],
                turrets_dmg_dealt=value["physical_dmg_dealt"] / value["games_played"],
                teammate_heals=value["teammate_heals"] / value["games_played"],
                teammate_shields=value["teammate_shields"] / value["games_played"],
                self_heal=value["self_heal"] / value["games_played"],
            )


