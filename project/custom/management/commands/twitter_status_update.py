import bitly_api
import datetime
import logging
import operator
import time
import tweepy
import urllib
import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.db.models import Q
from django.template import Context, Template
from django.utils.encoding import smart_str
from django.utils.timezone import utc

from custom.models import TwitterStatusUpdate, TwitterStatusUpdateLog, Profile
from twauth.models import TwitterUser

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Daemon to push twitter status updates'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.domain = Site.objects.get_current().domain

    def close_db_connection(self):
        from django import db
        db.close_connection()

    def status_update_error(self, e, twitter_user):
        if 'Invalid or expired token' in e.reason:
            twitter_user.status = False
            twitter_user.save()

    def handle(self, *args, **options):
        while True:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            twitter_status_updates = TwitterStatusUpdate.objects.filter(
                start_date__lte=now,
                end_date__gte=now,
            )
            if not twitter_status_updates.count():
                logger.info("No TwitterStatusUpdates available.")
                self.close_db_connection()
                time.sleep(300)
                continue

            for twitter_status_update in twitter_status_updates:
                twitter_users = TwitterUser.objects.filter(status=True, user__is_active=True)

                # Group Filtering
                try:
                    groups_qs = reduce(operator.or_, (Q(user__groups__id=id) for id in twitter_status_update.groups.values_list('pk', flat=True)))
                    twitter_users = twitter_users.filter(groups_qs)
                except:
                    pass
                    
                # Exclude processed users
                tw_log = TwitterStatusUpdateLog.objects.filter(twitter_status_update=twitter_status_update)
                tw_log_users_pk_list = list(tw_log.values_list('user__pk', flat=True))
                if tw_log_users_pk_list:
                    twitter_users = twitter_users.exclude(user__pk__in=tw_log_users_pk_list)

                twitter_users_pk_list = list(twitter_users.values_list('user__pk', flat=True))

                if not twitter_users_pk_list:
                    logger.info("No twitter users available for status update %d" % twitter_status_update.pk)
                    continue

                profiles = Profile.objects.filter(
                    semaphore_twitter=False,
                    enable_twitter_updates=True,
                    user__is_active=True,
                    user__pk__in=twitter_users_pk_list,
                )
                profiles_pk_list = list(profiles.values_list('pk', flat=True))
                Profile.objects.filter(pk__in=profiles_pk_list).update(semaphore_twitter=True)
                profiles = Profile.objects.filter(pk__in=profiles_pk_list)
                for profile in profiles:
                    logger.info('Twitter status update %d activated for profile %d' % (twitter_status_update.pk, profile.pk))
                    try:
                        # Double check for dupes
                        dupe_check = TwitterStatusUpdateLog.objects.filter(user=profile.user, twitter_status_update=twitter_status_update)
                        if dupe_check.count():
                            raise Exception('Dupe twitter status update %d found for profile %d' % (twitter_status_update.pk, profile.pk))

                        bitly_connection = bitly_api.Connection(settings.BITLY_LOGIN, settings.BITLY_API_KEY)
                        url_query_params = {
                            'ur': str(profile.user.pk),
                            'utm_source': 'twitter',
                            'utm_medium': 'tweet',
                            'utm_content': str(profile.user.pk),
                            'utm_campaign': 'twitter_status_update'
                        }
                        if twitter_status_update.link:
                            url = twitter_status_update.link
                            if self.domain in twitter_status_update.link:
                                url_parts = list(urlparse.urlparse(url))
                                query = dict(urlparse.parse_qsl(url_parts[4]))
                                query.update(url_query_params)
                                url_parts[4] = urllib.urlencode(query)
                                url = urlparse.urlunparse(url_parts)
                        else:
                            url = 'http://%s?%s' % (self.domain, urllib.urlencode(url_query_params))
                        bitly_results = bitly_connection.shorten(url)
                        if not bitly_results.get('url'):
                            raise Exception("Unable to get url, %s, shortend with bit.ly" % url)
                        short_link = bitly_results.get('url')

                        context = Context({"short_link": short_link,})
                        template = Template(twitter_status_update.content)
                        twitter_content = smart_str(template.render(context)).strip()
                        twitter_user = TwitterUser.objects.get(user=profile.user)
                        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
                        auth.set_access_token(twitter_user.oauth_token, twitter_user.oauth_token_secret)
                        api = tweepy.API(auth_handler=auth, api_root='/1.1')
                        try:
                            api.update_status(status=twitter_content)
                        except tweepy.TweepError, e:
                            self.status_update_error(e, twitter_user)
                            raise Exception('Error pushing twitter status update for user id %d. Error: %s' % (profile.user.pk, str(e)))
                        logger.info('Successfully sent twitter status update %d to profile %d' % (twitter_status_update.pk, profile.pk))
                        TwitterStatusUpdateLog.objects.create(user=profile.user, twitter_status_update=twitter_status_update)
                    except Exception, e:
                        logger.error('%s' % e)
                    finally:
                        profile.semaphore_twitter = False
                        profile.save()
                    time.sleep(1)
            self.close_db_connection()
            time.sleep(300)