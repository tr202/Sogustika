import sqlite3

from django.core.management import BaseCommand

from recipes.models import MeasurementUnit


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            import pandas as pd
        except Exception as e:
            print('Unable to import pandas', e)
        conn = sqlite3.connect('./db.sqlite3')
        conn.cursor()
        self.handle_1(conn, pd)
        

    def handle_1(self, conn, pd):
        try:
            df = pd.read_csv('/home/marid/Dev/foodgram-project-react/data/ingredients1.csv', usecols=[1])
            df.drop_duplicates(keep='first', inplace=True)
            df = df.assign(counted=True)
            df.to_sql('recipes_measurementunit', conn, if_exists='append',
                        index=False, chunksize=10000)
        except Exception as e:
            print('units', e)
        try:
            qs = MeasurementUnit.objects.values_list('id','unit')
            res = dict((v,k) for k,v in dict(qs).items())
            df = pd.read_csv('/home/marid/Dev/foodgram-project-react/data/ingredients1.csv')
            #df = df.assign(measurement_unit_id = res.get('unit'))
            df['measurement_unit_id'] = df['unit'].map(res)
            df = df.drop('unit', axis=1)
            df.to_sql('recipes_ingredient', conn, if_exists='append',
                        index=False, chunksize=10000)
        except Exception as e:
            print('ingredients', e)
        