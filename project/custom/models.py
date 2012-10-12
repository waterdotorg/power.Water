import facebook
import requests
import urllib

from django.contrib.auth.models import User
from django.core.files.base import File
from django.db import models
from django.db.models.signals import post_save

from fbauth.models import FacebookUser
from twauth.models import TwitterUser

def get_profile_image_path(instance, filename):
    extension = filename.split('.')[-1]
    dir = "profile-pics/%s/profile-photo.%s" % (instance.user.id, extension)
    return dir

class Profile(models.Model):
    DEFAULT_TYPE = 0
    TEST_TYPE = 1

    TYPE_CHOICES = (
        (DEFAULT_TYPE, 'Default'),
        (TEST_TYPE, 'Test'),
    )

    user = models.OneToOneField(User)
    followers = models.IntegerField(default=0)
    image = models.ImageField(upload_to=get_profile_image_path, max_length=256, blank=True)
    user_referrer = models.ForeignKey(User, related_name='user_referrer', blank=True, null=True)
    source_referrer = models.CharField(max_length=100, blank=True)
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    semaphore_twitter = models.BooleanField(default=False)
    semaphore_facebook = models.BooleanField(default=False)
    social_data_completed = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % self.user

    def social_data_process(self):
        try:
            facebook_user = FacebookUser.objects.get(user=self.user)

            # FB Profile Image
            fb_image_url = 'http://graph.facebook.com/' + str(facebook_user.uid) + '/picture?type=large'
            fb_image = urllib.urlretrieve(fb_image_url)
            if fb_image[0]:
                fb_image_contents = File(open(fb_image[0]))
                self.image.save('profile-image.png', fb_image_contents, save=True)

            # FB Followers Count
            fql_query = 'SELECT friend_count FROM user WHERE uid=me()'
            r = requests.get('https://graph.facebook.com/fql', params={'q': fql_query, 'access_token': facebook_user.access_token})
            if r.json['data'][0]['friend_count']:
                self.followers = r.json['data'][0]['friend_count']

            self.social_data_completed = True
            self.save()
        except:
            pass

        try:
            TwitterUser.objects.get(user=self.user)
        except:
            pass


### Signals ###
def post_save_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(post_save_user, sender=User)

def post_save_profile(sender, instance, created, **kwargs):
    if created or not instance.social_data_completed:
        instance.social_data_process()

post_save.connect(post_save_profile, sender=Profile)
