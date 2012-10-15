import facebook
import requests
import tweepy
import urllib

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth.signals import user_logged_in
from django.core.files.base import File
from django.db import models

from fbauth.models import FacebookUser
from twauth.models import TwitterUser

class TwitterStatusUpdate(models.Model):
    link = models.URLField(blank=True, help_text="Homepage url used if blank. Use absolute url's with trailing slash - http://example.com/foobar/")
    content = models.TextField(help_text="Context variables: {{ short_link }}")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    groups = models.ManyToManyField(Group, verbose_name='groups', help_text='Leave blank for everybody.', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s (%s - %s)" % (self.text.strip(), self.start_date, self.end_date)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date > self.end_date:
            raise ValidationError('Start date may not be after end date.')

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='post', max_length=256)
    content = models.TextField()
    published_date = models.DateTimeField()
    homepage = models.BooleanField(default=True, help_text='Display on homepage.')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('post', (), {'slug': self.slug,})

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
                self.followers = int(r.json['data'][0]['friend_count'])

            self.social_data_completed = True
            self.save()
        except:
            pass

        try:
            twitter_user = TwitterUser.objects.get(user=self.user)
            auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(twitter_user.oauth_token, twitter_user.oauth_token_secret)
            api = tweepy.API(auth_handler=auth, api_root='/1.1')

            # TW Profile Image
            tweepy_user = api.get_user(screen_name=auth.get_username())
            partition = tweepy_user.profile_image_url.rpartition('_normal')
            if partition[0]:
                profile_image_url = partition[0] + partition[2]
            else:
                profile_image_url = tweepy_user.profile_image_url
            tw_image = urllib.urlretrieve(profile_image_url)
            if tw_image[0]:
                tw_image_contents = File(open(tw_image[0]))
                self.image.save('profile-image.png', tw_image_contents, save=True)

            # TW Followers Count
            if tweepy_user.followers_count:
                self.followers = int(tweepy_user.followers_count)

            self.social_data_completed = True
            self.save()
        except:
            pass


### Signals ###
def user_signed_in(sender, request, user, **kwargs):
    try:
        profile = user.get_profile()
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()

    if not profile.social_data_completed:
        profile.social_data_process()

user_logged_in.connect(user_signed_in)