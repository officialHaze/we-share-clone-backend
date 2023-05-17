'''
django command to wait for the database to be available
'''


import time
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    '''django command to wait for the db'''

    def handle(self, *args, **options):
        '''entrypoint for the command'''
        self.stdout.write("Waiting for DB..")
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except(OperationalError, Psycopg2Error):
                self.stdout.write("DB not ready..waiting 1sec...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))
        