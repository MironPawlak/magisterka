from os.path import join
from django.conf import settings

from django.core.management import BaseCommand
import json

from apps.matches.models import Champion


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = join(settings.BASE_DIR, 'champions.json')
        with open(path, "r") as json_file:
            data = json.load(json_file)
            for name in data["data"]:
                if not Champion.objects.filter(name=name).exists():
                    Champion.objects.create(name=data["data"][name]["name"], key=data["data"][name]["key"],
                                            riot_id=data["data"][name]["id"])

