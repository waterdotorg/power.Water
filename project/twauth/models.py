from django.contrib.auth.models import User
from django.db import models

class TwitterUser(models.Model):
    user = models.ForeignKey(User, related_name='twitter')
    uid = models.CharField(max_length=20, unique=True)
    oauth_token = models.CharField(max_length=500, blank=True, db_index=True)
    oauth_token_secret = models.CharField(max_length=500, blank=True, db_index=True)
    status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'uid'))