import datetime
import logging
import facebook
import requests
import time

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.utils.timezone import utc

from custom.models import FacebookOGReferredLog, Profile
from fbauth.models import FacebookUser

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Facebook Open Graph - new friend joined daemon'
    args = ''

    def __init__(self):
        super(Command, self).__init__()
        self.domain = Site.objects.get_current().domain
        self.app_access_token = self.get_app_access_token()
        self.graph_action = settings.FACEBOOK_APP_NAMESPACE + ':recruit'

    def get_app_access_token(self):
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_API_SECRET,
            'grant_type': 'client_credentials',
        }
        r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        return r.text.replace('access_token=', '')

    def handle(self, *args, **options):
        while True:
            last_hour = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(hours=1)
            facebook_users = FacebookUser.objects.filter(status=True)
            facebook_users_list = list(facebook_users.values_list('user__pk', flat=True))
            profiles = Profile.objects.filter(user_referrer__in=facebook_users_list, user__date_joined__gte=last_hour)

            for profile in profiles:
                try:
                    FacebookOGReferredLog.objects.get(user=profile.user_referrer, user_referred=profile.user)
                except FacebookOGReferredLog.DoesNotExist:
                    try:
                        facebook_user = FacebookUser.objects.get(user=profile.user_referrer)
                        Profile.objects.get(user=facebook_user.user, enable_facebook_updates=True)
                        graph = facebook.GraphAPI(self.app_access_token)
                        graph.put_object(
                            facebook_user.uid,
                            self.graph_action,
                            friend='http://%s?ur=%d&du=%d' % (self.domain, profile.user_referrer.pk, profile.user.pk)
                        )
                        FacebookOGReferredLog.objects.create(user=profile.user_referrer, user_referred=profile.user)
                    except Exception, e:
                        FacebookOGReferredLog.objects.create(
                            user=profile.user_referrer,
                            user_referred=profile.user,
                            success=False,
                        )
                        logger.info("Error pushing Facebook OG new friend joined %s" % e)
            time.sleep(600)