from django.core.management import BaseCommand

from apps.matches.management.commands.create_csv import translate_champions, unpack


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv_name = "comp.csv"
        with open(csv_name, 'w', newline='') as csvfile:
            champions = translate_champions(
                ["Garen", "Viego", "Zed", "Sivir", "Rell"],
                ["Camille","Anivia", "KogMaw" ],
                "riot_id")

            csvfile.write(f"{unpack(champions)}\n")
