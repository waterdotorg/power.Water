import datetime
import logging
import time

from django.core.management.base import BaseCommand
from django.utils.timezone import utc
from custom.models import Profile

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Daemon to update social data'
    args = ''

    def close_db_connection(self):
        from django import db
        db.close_connection()

    def handle(self, *args, **options):
        while True:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)

            profiles = Profile.objects.filter(
                updated_date__lt=now - datetime.timedelta(days=30),
                user__is_active=True,
            ).order_by('updated_date')

            for profile in profiles:
                profile.social_data_process()
                profile.save() # Force updated date to today
                time.sleep(60)

            self.close_db_connection()
            time.sleep(3600)