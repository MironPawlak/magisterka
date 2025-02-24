from datetime import datetime

from django.db import models

POSITION_CHOICES = [
    ("TOP", "Top"),
    ("JGL", "Jungle"),
    ("MID", "Middle"),
    ("BOT", "Bottom"),
    ("SUP", "Support")
]


class Match(models.Model):
    riot_id = models.CharField(max_length=128, unique=True)
    data = models.JSONField(null=True, blank=True)


class Player(models.Model):
    puuid = models.CharField(max_length=128, unique=True)
    last_update = models.DateTimeField(default=datetime(2025, 1, 9))


class Champion(models.Model):
    key = models.IntegerField(unique=True)
    riot_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128, unique=True)
    position = models.CharField(max_length=64, blank=True, null=True, choices=POSITION_CHOICES)


class Statistic(models.Model):
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    bans = models.IntegerField(default=0)


class MatchChampion(models.Model):
    champion = models.ForeignKey("matches.Champion", on_delete=models.CASCADE)
    match = models.ForeignKey("matches.SimpleMatch", on_delete=models.CASCADE)
    team_id = models.IntegerField()
    win = models.BooleanField()


class SimpleMatch(models.Model):
    riot_id = models.CharField(max_length=128, unique=True)
    date = models.DateTimeField()
    won = models.BooleanField(null=True, blank=True)
    game_duration = models.IntegerField(null=True, blank=True)
    gold_difference = models.IntegerField(null=True, blank=True)
    kill_difference = models.IntegerField(null=True, blank=True)
    exp_difference = models.IntegerField(null=True, blank=True)
    picks = models.ManyToManyField(Champion, through=MatchChampion)
    bans = models.ManyToManyField(Champion, related_name="bans")

    class Meta:
        indexes = [
            models.Index(fields=['date'], name='date_idx'),
        ]


class ChampionClass(models.Model):
    champion = models.OneToOneField("matches.Champion", on_delete=models.CASCADE, related_name="champ_class")
    gold_earned = models.DecimalField(max_digits=15, decimal_places=5)
    experience = models.DecimalField(max_digits=15, decimal_places=5)
    kills = models.DecimalField(max_digits=15, decimal_places=5)
    deaths = models.DecimalField(max_digits=15, decimal_places=5)
    assists = models.DecimalField(max_digits=15, decimal_places=5)
    time_ccing = models.DecimalField(max_digits=15, decimal_places=5)
    total_cc_time = models.DecimalField(max_digits=15, decimal_places=5)
    turret_takedowns = models.DecimalField(max_digits=15, decimal_places=5)
    true_dmg_taken = models.DecimalField(max_digits=15, decimal_places=5)
    magic_dmg_taken = models.DecimalField(max_digits=15, decimal_places=5)
    physical_dmg_taken = models.DecimalField(max_digits=15, decimal_places=5)
    self_dmg_mitigated = models.DecimalField(max_digits=15, decimal_places=5)
    true_dmg_dealt = models.DecimalField(max_digits=15, decimal_places=5)
    magic_dmg_dealt = models.DecimalField(max_digits=15, decimal_places=5)
    physical_dmg_dealt = models.DecimalField(max_digits=15, decimal_places=5)
    turrets_dmg_dealt = models.DecimalField(max_digits=15, decimal_places=5)
    teammate_heals = models.DecimalField(max_digits=15, decimal_places=5)
    teammate_shields = models.DecimalField(max_digits=15, decimal_places=5)
    self_heal = models.DecimalField(max_digits=15, decimal_places=5)


class ChampionCounters(models.Model):
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE)
    counters = models.JSONField()


class PredictionLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=256, null=True, blank=True)
    position = models.CharField(max_length=256)
    allies = models.JSONField()
    enemies = models.JSONField()
    bans = models.JSONField()
    predicitons = models.JSONField()
