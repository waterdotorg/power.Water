import bitly_api
import datetime
import facebook
import logging
import multiprocessing
import operator
import requests
import signal
import sys
import time
import urllib
import urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.encoding import smart_str
from django.utils.timezone import utc

from custom.models import FacebookStatusUpdate, FacebookStatusUpdateLog, \
    Profile
from fbauth.models import FacebookUser

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Daemon to push facebook status updates'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.num_processes = multiprocessing.cpu_count()
        self.work_queue = multiprocessing.Queue()
        self.domain = Site.objects.get_current().domain
        self.app_access_token = self.get_app_access_token()

    def get_app_access_token(self):
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_API_SECRET,
            'grant_type': 'client_credentials',
        }
        r = requests.get(
            'https://graph.facebook.com/v2.0/oauth/access_token',
            params=params
        )
        return r.text.replace('access_token=', '')

    def graph_api_error_handle(self, e, facebook_user):
        if e.result.get('error'):
            if e.result['error'].get('type') == 'OAuthException':
                facebook_user.status = False
                facebook_user.save()

    def worker(self, *args, **kwargs):
        while True:
            try:
                queue = self.work_queue.get_nowait()
                profile = Profile.objects.get(pk=queue['profile_pk'])
                facebook_status_update = FacebookStatusUpdate.objects.get(
                    pk=queue['facebook_status_update_pk']
                )
                logger.info(
                    'Facebook status update %d activated for profile %d'
                    % (facebook_status_update.pk, profile.pk)
                )
            except:
                logger.info('No facebook status updates found in queue')
                time.sleep(30)
                continue

            try:
                # Double check for dupes
                dupe_check = FacebookStatusUpdateLog.objects.filter(
                    user=profile.user,
                    facebook_status_update=facebook_status_update
                )
                if dupe_check.count():
                    raise Exception(
                        'Dupe facebook status update %d found for profile %d'
                        % (facebook_status_update.pk, profile.pk)
                    )

                bitly_connection = bitly_api.Connection(settings.BITLY_LOGIN,
                                                        settings.BITLY_API_KEY)
                url_query_params = {
                    'ur': str(profile.user.pk),
                    'utm_source': 'facebook',
                    'utm_medium': 'wall',
                    'utm_content': str(profile.user.pk),
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
                    url = 'http://%s?%s' % (self.domain,
                                            urllib.urlencode(url_query_params))
                bitly_results = bitly_connection.shorten(url)
                if not bitly_results.get('url'):
                    raise Exception(
                        "Unable to get url, %s, shortend with bit.ly"
                        % url
                    )
                short_link = bitly_results.get('url')

                attachment = {
                    "name": smart_str(facebook_status_update.name).strip(),
                    "link": short_link,
                    "picture": "http://%s%s" % (self.domain,facebook_status_update.picture.url),
                    "caption": smart_str(facebook_status_update.caption).strip(),
                    "description": smart_str(facebook_status_update.description).strip(),
                }
                facebook_user = FacebookUser.objects.get(user=profile.user)
                graph = facebook.GraphAPI(self.app_access_token)
                try:
                    graph.put_wall_post(message='', attachment=attachment, profile_id=facebook_user.uid)
                except facebook.GraphAPIError, e:
                    self.graph_api_error_handle(e, facebook_user)
                    raise Exception('Error pushing facebook post to wall of user id %d. Error: %s' % (profile.user.pk, str(e)))

                logger.info('Successfully sent facebook status update %d to profile %d' % (facebook_status_update.pk, profile.pk))
                FacebookStatusUpdateLog.objects.create(user=profile.user, facebook_status_update=facebook_status_update)
            except Exception, e:
                logger.error('%s' % e)
            finally:
                profile.semaphore_facebook = False
                profile.save()


    def handle(self, *args, **options):
        # catch TERM signal to allow finalizers to run and reap daemonic children
        signal.signal(signal.SIGTERM, lambda *args: sys.exit(-signal.SIGTERM))

        try:
            for i in range(self.num_processes):
                p = multiprocessing.Process(target=self.worker)
                p.daemon = True
                p.start()
        except:
            logger.error("Error initiating facebook_status_update multiprocessing workers")
            raise

        while True:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            facebook_status_updates = FacebookStatusUpdate.objects.filter(
                start_date__lte=now,
                end_date__gte=now,
            )
            if not facebook_status_updates.count():
                logger.info("No FacebookStatusUpdates available.")
                time.sleep(300)
                continue

            for facebook_status_update in facebook_status_updates:
                facebook_users = FacebookUser.objects.filter(status=True)

                # Group Filtering
                try:
                    groups_qs = reduce(operator.or_, (Q(user__groups__id=id) for id in facebook_status_update.groups.values_list('pk', flat=True)))
                    facebook_users = facebook_users.filter(groups_qs)
                except:
                    pass

                # Exclude processed users
                fb_log = FacebookStatusUpdateLog.objects.filter(facebook_status_update=facebook_status_update)
                fb_log_users_pk_list = list(fb_log.values_list('user__pk', flat=True))
                if fb_log_users_pk_list:
                    facebook_users = facebook_users.exclude(user__pk__in=fb_log_users_pk_list)

                facebook_users_pk_list = list(facebook_users.values_list('user__pk', flat=True))

                if not facebook_users_pk_list:
                    logger.info("No facebook users available for status update %s" % facebook_status_update)
                    continue

                profiles = Profile.objects.filter(
                    semaphore_facebook=False,
                    enable_facebook_updates=True,
                    user__is_active=True,
                    user__pk__in=facebook_users_pk_list
                )
                profiles_pk_list = list(profiles.values_list('pk', flat=True))
                Profile.objects.filter(pk__in=profiles_pk_list).update(semaphore_facebook=True)
                profiles = Profile.objects.filter(pk__in=profiles_pk_list)
                for profile in profiles:
                    self.work_queue.put({'profile_pk': profile.pk, 'facebook_status_update_pk': facebook_status_update.pk})
                    logger.info("Added profile %d and facebook status update %d to queue" % (profile.pk, facebook_status_update.pk))
                    time.sleep(1)

            time.sleep(300)
