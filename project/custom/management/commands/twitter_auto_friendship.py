import logging
import time
import tweepy

from django.conf import settings
from django.core.management.base import BaseCommand

from custom.models import TwitterAutoFriendshipLog
from twauth.models import TwitterUser

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Twitter auto friendship daemon'
    args = ''

    def close_db_connection(self):
        from django import db
        db.close_connection()

    def handle(self, *args, **options):
        while True:
            twitter_users = TwitterUser.objects.filter(status=True, user__is_active=True)
            # Exclude Processed Users
            taf_logs = TwitterAutoFriendshipLog.objects.all()
            users_pk_list = list(taf_logs.values_list('user__pk', flat=True))
            if users_pk_list:
                twitter_users = twitter_users.exclude(user__pk__in=users_pk_list)

            if twitter_users.count():
                for twitter_user in twitter_users:
                    try:
                        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
                        auth.set_access_token(twitter_user.oauth_token, twitter_user.oauth_token_secret)
                        api = tweepy.API(auth_handler=auth, api_root='/1.1')
                        api.create_friendship(screen_name=settings.TWITTER_SCREEN_NAME)
                        TwitterAutoFriendshipLog.objects.create(user=twitter_user.user)
                    except:
                        TwitterAutoFriendshipLog.objects.create(user=twitter_user.user, success=False)
            self.close_db_connection()
            time.sleep(300)