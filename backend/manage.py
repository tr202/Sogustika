#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sogustika.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    comm = sys.argv
    if 'import_csv' in sys.argv:
        comm = ['manage.py']
    print('comm', sys.argv)
    execute_from_command_line(comm)
    if 'import_csv' in sys.argv:
        try:
            from api.management.commands.load_csv_data import Command as sqlite
            sqlite().handle()
        except Exception as e:
            print('sqlite fail', e)
        try:
            from api.management.commands.load_data import Command as postgres
            postgres().handle()
        except Exception as e:
            print('postgres fail', e)    
    


if __name__ == '__main__':
    main()
    
