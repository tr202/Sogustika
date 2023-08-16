import json

from decouple import config
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(config("PATH_TO_JSON")) as file:
            Ingredient.objects.bulk_create(
                map(lambda x: Ingredient(**x), json.load(file))
            )
