import os
import requests
import shutil
import tweepy
import urllib

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth.signals import user_logged_in
from django.core.files.base import File
from django.db import models

from fbauth.models import FacebookUser
from twauth.models import TwitterUser

class FacebookStatusUpdate(models.Model):
    link = models.URLField(blank=True, help_text="Homepage url used if blank. Use absolute url's with trailing slash - http://example.com/foobar/")
    picture = models.ImageField(upload_to="facebook-status-update")
    name = models.CharField(max_length=100, help_text="The name of the link")
    caption = models.CharField(max_length=100, help_text="The caption of the link which appears beneath the link name", blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    groups = models.ManyToManyField(Group, verbose_name='groups', help_text='Leave blank for everybody.', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s" % self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date > self.end_date:
            raise ValidationError('Start date may not be after end date.')

class FacebookStatusUpdateLog(models.Model):
    facebook_status_update = models.ForeignKey(FacebookStatusUpdate)
    user = models.ForeignKey(User)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('facebook_status_update', 'user')

class TwitterStatusUpdate(models.Model):
    link = models.URLField(blank=True, help_text="Homepage url used if blank. Use absolute url's with trailing slash - http://example.com/foobar/")
    content = models.TextField(help_text="Context variables: {{ short_link }}")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    groups = models.ManyToManyField(Group, verbose_name='groups', help_text='Leave blank for everybody.', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s" % self.content

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date > self.end_date:
            raise ValidationError('Start date may not be after end date.')

class TwitterStatusUpdateLog(models.Model):
    twitter_status_update = models.ForeignKey(TwitterStatusUpdate)
    user = models.ForeignKey(User)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('twitter_status_update', 'user')

class TwitterAutoFriendshipLog(models.Model):
    user = models.ForeignKey(User)
    success = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s Auto Friend" % self.user

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
    user = models.OneToOneField(User)
    followers = models.IntegerField(default=0)
    image = models.ImageField(upload_to=get_profile_image_path, max_length=256, blank=True)
    user_referrer = models.ForeignKey(User, related_name='user_referrer', blank=True, null=True)
    source_referrer = models.CharField(max_length=100, blank=True)
    semaphore_twitter = models.BooleanField(default=False)
    semaphore_facebook = models.BooleanField(default=False)
    social_data_completed = models.BooleanField(default=False)
    enable_facebook_updates = models.BooleanField(default=True)
    enable_twitter_updates = models.BooleanField(default=True)
    enable_email_updates = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.user

    def remove_profile_images(self):
        if self.image:
            user_profile_pic_path = settings.MEDIA_ROOT + '/profile-pics/' + str(self.user.pk)
            if os.path.isdir(user_profile_pic_path):
                    shutil.rmtree(user_profile_pic_path)
            self.image.delete()

    def social_data_process(self):
        if not self.user.is_active:
            return None

        try:
            facebook_user = FacebookUser.objects.get(user=self.user, status=True)

            # FB Profile Image
            fb_image_url = 'http://graph.facebook.com/' + str(facebook_user.uid) + '/picture?type=large'
            fb_image = urllib.urlretrieve(fb_image_url)
            if fb_image[0]:
                fb_image_contents = File(open(fb_image[0]))
                if self.image:
                    self.remove_profile_images()
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
            twitter_user = TwitterUser.objects.get(user=self.user, status=True)
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
                if self.image:
                    self.remove_profile_images()
                self.image.save('profile-image.png', tw_image_contents, save=True)

            # TW Followers Count
            if tweepy_user.followers_count:
                self.followers = int(tweepy_user.followers_count)

            self.social_data_completed = True
            self.save()
        except:
            pass

    def promoted_posts_count(self):
        t = TwitterStatusUpdateLog.objects.filter(user=self.user).count()
        f = FacebookStatusUpdateLog.objects.filter(user=self.user).count()
        return int(t+f)

    def friends_joined_count(self):
        return int(Profile.objects.filter(user_referrer=self.user).count())

    def friends_joined(self, limit=3):
        friend_profiles = Profile.objects.filter(user_referrer=self.user).order_by('-pk')[:limit]
        return friend_profiles

class FacebookOGReferredLog(models.Model):
    user = models.ForeignKey(User, related_name='user')
    user_referred = models.ForeignKey(User, related_name='user_referred')
    success = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'user_referred'))

    def __unicode__(self):
        return "%s - %s" % (self.user, self.user_referred)

class FriendJoinedEmailLog(models.Model):
    user = models.ForeignKey(User, related_name='user_fje')
    user_referred = models.ForeignKey(User, related_name='user_referred_fje')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'user_referred'))

    def __unicode__(self):
        return "%s - %s" % (self.user, self.user_referred)

### Signals ###
def user_signed_in(sender, request, user, **kwargs):
    try:
        profile = user.get_profile()
    except Profile.DoesNotExist:
        user_referrer = None
        if request.session.get('ur'):
            try:
                user_referrer = User.objects.get(id=request.session.get('ur'))
            except:
                user_referrer = None
            del request.session['ur']

        source_referrer = request.session.get('sr')
        if source_referrer:
            del request.session['sr']

        profile = Profile(user=user,)
        if user_referrer:
            profile.user_referrer = user_referrer
        if source_referrer:
            profile.source_referrer = source_referrer
        profile.save()

    if not profile.social_data_completed:
        profile.social_data_process()

user_logged_in.connect(user_signed_in)