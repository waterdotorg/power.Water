import datetime
import logging
import time

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.timezone import utc

from custom.models import Profile, FriendJoinedEmailLog

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Friend joined email daemon'
    args = ''

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.site = Site.objects.get_current()

    def handle(self, *args, **options):
        while True:
            last_hour = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(hours=1)
            profiles = Profile.objects.select_related().filter(
                user__date_joined__gte=last_hour,
                user_referrer__profile__enable_email_updates=True,
                user_referrer__is_active=True,
            )
            for profile in profiles:
                if not profile.user_referrer.email:
                    continue

                try:
                    FriendJoinedEmailLog.objects.get(user=profile.user_referrer, user_referred=profile.user)
                except FriendJoinedEmailLog.DoesNotExist:
                    dict_context = {
                        'site': self.site,
                        'referred_profile': profile,
                        'referring_profile': profile.user_referrer.get_profile(),
                    }
                    email_subject = render_to_string('emails/friend-joined/subject.txt', dict_context).strip()
                    email_txt = render_to_string('emails/friend-joined/message.txt', dict_context)
                    email_html = render_to_string('emails/friend-joined/message.html', dict_context)
                    email = EmailMultiAlternatives(
                        email_subject, email_txt, settings.DEFAULT_FROM_EMAIL, [profile.user_referrer.email,]
                    )
                    email.attach_alternative(email_html, 'text/html')
                    email.send()
                    FriendJoinedEmailLog.objects.create(user=profile.user_referrer, user_referred=profile.user)
            time.sleep(600)