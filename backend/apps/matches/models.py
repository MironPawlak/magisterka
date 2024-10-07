from datetime import datetime

from django.db import models


class Match(models.Model):
    riot_id = models.CharField(max_length=128, unique=True)
    data = models.JSONField(null=True, blank=True)


class Player(models.Model):
    puuid = models.CharField(max_length=128, unique=True)
    # TODO Start of split, think about something else
    last_update = models.DateTimeField(default=datetime(2024, 9, 26))


class Champion(models.Model):
    key = models.IntegerField(unique=True)
    riot_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128, unique=True)


class Statistic(models.Model):
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    bans = models.IntegerField(default=0)
