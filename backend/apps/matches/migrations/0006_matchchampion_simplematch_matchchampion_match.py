# Generated by Django 4.1.4 on 2024-11-05 22:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0005_statistic'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchChampion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.IntegerField()),
                ('win', models.BooleanField()),
                ('champion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.champion')),
            ],
        ),
        migrations.CreateModel(
            name='SimpleMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('riot_id', models.CharField(max_length=128, unique=True)),
                ('date', models.DateTimeField()),
                ('bans', models.ManyToManyField(related_name='bans', to='matches.champion')),
                ('picks', models.ManyToManyField(through='matches.MatchChampion', to='matches.champion')),
            ],
        ),
        migrations.AddField(
            model_name='matchchampion',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.simplematch'),
        ),
    ]
