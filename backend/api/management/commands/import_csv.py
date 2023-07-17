from django.conf import settings
from django.core.management import BaseCommand

from .load_csv_data import Command as sqlite
from .load_data import Command as postgres


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            sqlite().handle(self, *args, **options)
        elif settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
            postgres.handle(self, *args, **options)
        else:
            raise Exception('Unknown database')
