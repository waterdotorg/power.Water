import bitly_api
import datetime
import facebook
import logging
import operator
import requests
import time
import urllib
import urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.encoding import smart_str
from django.utils.timezone import utc

from custom.models import FacebookStatusUpdate, FacebookStatusUpdateLog, Profile
from fbauth.models import FacebookUser

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Daemon to push facebook status updates'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.domain = Site.objects.get_current().domain
        self.app_access_token = self.get_app_access_token()

    def get_app_access_token(self):
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_API_SECRET,
            'grant_type': 'client_credentials',
        }
        r = requests.get('https://graph.facebook.com/v2.0/oauth/access_token', params=params)
        return r.text.replace('access_token=', '')

    def graph_api_error_handle(self, e, facebook_user):
        if e.result.get('error'):
            if e.result['error'].get('type') == 'OAuthException':
                facebook_user.status = False
                facebook_user.save()

    def close_db_connection(self):
        from django import db
        db.close_connection()

    def handle(self, *args, **options):
        while True:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            facebook_status_updates = FacebookStatusUpdate.objects.filter(
                start_date__lte=now,
                end_date__gte=now,
            )

            if not facebook_status_updates.count():
                logger.info("No FacebookStatusUpdates available.")
                self.close_db_connection()
                time.sleep(200)
                continue

            for facebook_status_update in facebook_status_updates:
                facebook_users = FacebookUser.objects.filter(
                    status=True,
                    user__is_active=True,
                    user__profile__semaphore_facebook=False,
                    user__profile__enable_facebook_updates=True
                ).exclude(user__facebookstatusupdatelog__facebook_status_update=facebook_status_update)

                # Group Filtering
                try:
                    groups_qs = reduce(operator.or_, (Q(user__groups__id=id) for id in facebook_status_update.groups.values_list('pk', flat=True)))
                    facebook_users = facebook_users.filter(groups_qs)
                except:
                    pass

                facebook_users_list = list(facebook_users[:150])

                if not facebook_users_list:
                    logger.info("No facebook users available for status update %s" % facebook_status_update)
                    continue

                user_id_list = [fu.user.pk for fu in facebook_users_list]

                Profile.objects.filter(user__pk__in=user_id_list).update(
                    semaphore_facebook=True
                )

                for facebook_user in facebook_users_list:
                    logger.info('Facebook status update %d activated for facebook user %d' % (facebook_status_update.pk, facebook_user.pk))

                    try:
                        """
                        ### Disable bit.ly due to API rate limitations ###

                        bitly_connection = bitly_api.Connection(settings.BITLY_LOGIN, settings.BITLY_API_KEY)
                        url_query_params = {
                            'ur': str(facebook_user.user.pk),
                            'utm_source': 'facebook',
                            'utm_medium': 'wall',
                            'utm_content': str(facebook_user.user.pk),
                            'utm_campaign': 'facebook_status_update'
                        }
                        if facebook_status_update.link:
                            url = facebook_status_update.link
                            if self.domain in facebook_status_update.link:
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
                        """

                        attachment = {
                            "name": smart_str(facebook_status_update.name).strip(),
                            "link": facebook_status_update.link,
                            "picture": "http://%s%s" % (self.domain, facebook_status_update.picture.url),
                            "caption": smart_str(facebook_status_update.caption).strip(),
                            "description": smart_str(facebook_status_update.description).strip(),
                        }
                        graph = facebook.GraphAPI(self.app_access_token)
                        try:
                            graph.put_wall_post(message='', attachment=attachment, profile_id=facebook_user.uid)
                        except facebook.GraphAPIError, e:
                            self.graph_api_error_handle(e, facebook_user)
                            raise Exception('Error pushing facebook post to wall of user id %d. Error: %s' % (facebook_user.user.pk, str(e)))

                        logger.info('Successfully sent facebook status update %d to facebook user %d' % (facebook_status_update.pk, facebook_user.pk))
                        FacebookStatusUpdateLog.objects.create(user=facebook_user.user, facebook_status_update=facebook_status_update)
                    except Exception, e:
                        logger.error('%s' % e)
                    finally:
                        profile = Profile.objects.get(user=facebook_user.user)
                        profile.semaphore_facebook = False
                        profile.save()
                    time.sleep(1)
            self.close_db_connection()
            time.sleep(200)
