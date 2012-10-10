import cgi
import facebook
import urllib

from django.config import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from fbauth.models import FacebookUser

class FbAuth(object):
    """
    Facebook Oauth2 Authentication Backend
    """
    def authenticate(self, verification_code=None):
        if not verification_code:
            return None

        access_token = None
        access_token_expires = None
        fb_profile = None
        domain = Site.objects.get_current().domain

        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': 'http://' + domain + reverse('fbauth'),
            'client_secret': settings.FACEBOOK_API_SECRET,
            'code': verification_code,
        }
        access_token_url = "https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)

        fb_response = cgi.parse_qs(urllib.urlopen(access_token_url).read())

        try:
            access_token = fb_response['access_token'][0]
        except:
            return None

        try:
            if fb_response.get('expires'):
                access_token_expires = fb_response['expires'][0]
        except:
            pass

        try:
            graph = facebook.GraphAPI(access_token)
            fb_profile = graph.get_object('me')
        except:
            return None

        try:
            facebook_user = FacebookUser.objects.get(uid=str(fb_profile['id']))
            facebook_user.access_token = access_token
            facebook_user.access_token_expires = access_token_expires
            facebook_user.status = True
            facebook_user.save()
        except FacebookUser.DoesNotExist:
            user, created = User.objects.get_or_create(username='fb_' + str(fb_profile['id']))
            user.email = fb_profile.get('email', '')
            user.first_name = fb_profile.get('first_name', '')
            user.last_name = fb_profile.get('last_name', '')
            user.set_unusable_password()
            user.save()

            facebook_user = FacebookUser(
                user=user,
                uid=str(fb_profile['id']),
                access_token=access_token,
                access_token_expires=access_token_expires,
                status=True,
            )
            facebook_user.save()

        return facebook_user.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None