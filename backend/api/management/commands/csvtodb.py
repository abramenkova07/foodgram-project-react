import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('D:/Dev/foodgram-project-react/data/ingredients.csv',
                  'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            Ingredient.objects.all().delete()
            for id, row in enumerate(reader, 1):
                Ingredient.objects.create(
                    id=id,
                    name=row[0],
                    measurement_unit=row[1]
                )
        self.stdout.write(self.style.SUCCESS(
            'Данные из "ingredients.csv" загружены в БД'))
