from rest_framework import serializers
from apps.matches.models import POSITION_CHOICES, Statistic, Champion


class PredictionInputSerializer(serializers.Serializer):
    position = serializers.ChoiceField(choices=POSITION_CHOICES)
    allies = serializers.ListField(child=serializers.IntegerField())
    enemies = serializers.ListField(child=serializers.IntegerField())
    bans = serializers.ListField(child=serializers.IntegerField())


class ChampionPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Champion
        fields = '__all__'


class PredictionSerializer(serializers.Serializer):
    champion = ChampionPredictionSerializer()
    predicted = serializers.FloatField()


class PredictionOutputSerializer(serializers.Serializer):
    current_prediction = serializers.FloatField()
    top_predictions = PredictionSerializer(many=True)


class CounterOutputSerializer(serializers.Serializer):
    champion = ChampionPredictionSerializer()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    ratio = serializers.FloatField()

class StatSerializer(serializers.Serializer):
    position = serializers.ChoiceField(choices=POSITION_CHOICES)


class ChampionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Champion
        fields = ("riot_id",)


class StatisticSerializer(serializers.ModelSerializer):
    ratio = serializers.FloatField()

    class Meta:
        model = Statistic
        fields = ("champion", "wins", "losses", "bans", "ratio")
        depth = 1
