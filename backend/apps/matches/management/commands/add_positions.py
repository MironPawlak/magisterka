from os.path import join
from django.conf import settings

from django.core.management import BaseCommand
import json

from apps.matches.models import Champion


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = join(settings.BASE_DIR, 'champions_position.json')
        with open(path, "r") as json_file:
            data = json.load(json_file)
            for champion in data:
                c = Champion.objects.filter(name=champion["name"]).first()
                c.position = champion["position"]
                c.save()
