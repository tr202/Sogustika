from sqlalchemy import create_engine

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import MeasurementUnit


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            import pandas as pd
        except Exception as e:
            print('Unable to import pandas', e)

        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        database_name = settings.DATABASES['default']['NAME']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        struct = 'postgresql://{user}:{password}@{host}:{port}/{database_name}'
        database_url = struct.format(user=user,
                                     password=password,
                                     host=host,
                                     port=port,
                                     database_name=database_name,)

        engine = create_engine(database_url, echo=False)

        self.handle_1(engine, pd)

    def handle_1(self, engine, pd):
        try:
            df = pd.read_csv(
                settings.BASE_DIR / 'data/ingredients1.csv',
                usecols=[1]
            )
            df.drop_duplicates(keep='first', inplace=True)
            df = df.assign(counted=True)
            df.to_sql('recipes_measurementunit',
                      engine, if_exists='append',
                      index=False)
        except Exception as e:
            print('units', e)
        try:
            qs = MeasurementUnit.objects.values_list('id', 'unit')
            res = dict((v, k) for k, v in dict(qs).items())
            df = pd.read_csv(
                settings.BASE_DIR / 'data/ingredients1.csv'
            )
            df['measurement_unit_id'] = df['unit'].map(res)
            df = df.drop('unit', axis=1)
            df.to_sql('recipes_ingredient',
                      engine, if_exists='append',
                      index=False)
        except Exception as e:
            print('ingredients', e)
