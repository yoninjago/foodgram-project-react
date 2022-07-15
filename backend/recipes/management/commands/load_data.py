import json
import os

from foodgram.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from recipes.models import Ingredient

DATA_ROOT = os.path.join(BASE_DIR, 'data')
DEFAULT_FILENAME = 'ingredients.json'


class Command(BaseCommand):
    help = 'load data from json'

    def add_arguments(self, parser):
        parser.add_argument('filename', default=DEFAULT_FILENAME, nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(os.path.join(DATA_ROOT, options['filename']), 'r',
                      encoding='utf-8') as file:
                for ingredient in json.load(file):
                    try:
                        Ingredient.objects.create(
                            name=ingredient['name'],
                            measurement_unit=ingredient['measurement_unit']
                            )
                    except IntegrityError:
                        print(f'Ошибка! Ингридиет {ingredient["name"]} '
                              f'({ingredient["measurement_unit"]}) '
                              f'уже присутствует БД')

        except FileNotFoundError as error:
            raise CommandError(error)
