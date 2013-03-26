import datetime
import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import utc

from instagram.client import InstagramAPI
from instagallery.models import Tag, Image

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Instagram hashtag gallery'
    args = ''

    def close_db_connection(self):
        from django import db
        db.close_connection()

    def update_tag(self, tag):
        tag.semaphore = False
        tag.save()

    def handle(self, *args, **options):
        while True:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            api = InstagramAPI(client_id=settings.INSTAGRAM_CLIENT_ID)

            tags = Tag.objects.filter(
                semaphore=False,
                last_processed_date__lte=now-datetime.timedelta(seconds=900),
            )
            for tag in tags:
                tag.last_processed_date = now
                tag.semaphore = True
                tag.save()

                try:
                    insta_result = api.tag_recent_media(100, None, tag.tag)
                except:
                    self.update_tag(tag)
                    continue

                for media in insta_result[0]:
                    try:
                        Image.objects.get(tag=tag, instagram_id=media.id)
                        break
                    except Image.DoesNotExist:
                        image = Image(
                            tag=tag,
                            instagram_id=media.id,
                            link=media.link,
                            thumbnail_url=media.images['thumbnail'].url,
                        )
                        image.save()
                self.update_tag(tag)

            self.close_db_connection()
            time.sleep(300)