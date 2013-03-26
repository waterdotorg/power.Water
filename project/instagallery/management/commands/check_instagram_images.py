import logging
import requests
import time

from django.core.management.base import BaseCommand
from instagallery.models import Image

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check instagram images'
    args = ''

    def close_db_connection(self):
        from django import db
        db.close_connection()

    def handle(self, *args, **options):
        while True:
            instagram_images = Image.objects.order_by('-instagram_id')[:200]

            for image in instagram_images:
                try:
                    r = requests.get(image.link)
                    if r.status_code == 404:
                        image.delete()
                except:
                    pass
                time.sleep(2)

            self.close_db_connection()
            time.sleep(1800)