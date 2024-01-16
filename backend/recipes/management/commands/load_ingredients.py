import csv
import os

from django.core.management.base import BaseCommand

from ...models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from the CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        csv_file_path = os.path.abspath(
            os.path.join(options['path'], 'ingredients.csv'))

        self.create_ingredients(csv_file_path)
        self.stdout.write(self.style.SUCCESS(
            'Ingredients loaded successfully.')
        )

    def create_ingredients(self, csv_file_path):
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                if len(row) != 2:
                    continue

                name, measurement_unit = row

                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
