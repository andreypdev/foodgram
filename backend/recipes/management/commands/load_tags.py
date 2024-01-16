import csv
import os

from django.core.management.base import BaseCommand

from ...models import Tag


class Command(BaseCommand):
    help = 'Load tags from CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        csv_file_path = os.path.abspath(
            os.path.join(options['path'], 'tags.csv'))

        self.create_ingredients(csv_file_path)
        self.stdout.write(self.style.SUCCESS(
            'Tags loaded successfully.')
        )

    def create_ingredients(self, csv_file_path):
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                if len(row) != 3:
                    continue

                name, color, slug = row

                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )
