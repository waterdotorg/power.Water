import tweepy

from django.contrib.auth.models import User

from twauth.models import TwitterUser

class TwAuth(object):
    """
    Twitter Oauth Authentication Backend
    """
    def authenticate(self, oauth_handler=None):
        if not oauth_handler:
            return None

        try:
            api = tweepy.API(oauth_handler)
            tw_user_data = api.verify_credentials()
        except:
            return None

        try:
            tw_user = TwitterUser.objects.get(uid=tw_user_data.id)
            tw_user.oauth_token = oauth_handler.access_token.key
            tw_user.oauth_token_secret = oauth_handler.access_token.secret
            tw_user.status = True
            tw_user.save()
        except TwitterUser.DoesNotExist:
            user, created = User.objects.get_or_create(username='tw_' + str(tw_user_data.id))
            try:
                split_name = tw_user_data.name.split(None, 1)
                user.first_name = split_name[0]
                user.last_name = split_name[1]
            except:
                pass
            user.set_unusable_password()
            user.save()

            tw_user = TwitterUser(
                user=user,
                uid=str(tw_user_data.id),
                oauth_token=oauth_handler.access_token.key,
                oauth_token_secret=oauth_handler.access_token.secret,
                status=True,
            )
            tw_user.save()

        return tw_user.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None