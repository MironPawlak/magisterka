# Generated by Django 4.1.4 on 2024-10-04 01:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='riot_id',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 26, 0, 0)),
        ),
        migrations.AlterField(
            model_name='player',
            name='puuid',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
