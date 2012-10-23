from django.contrib.auth.models import User
from django.db import models

class FacebookUser(models.Model):
    user = models.ForeignKey(User, related_name='facebook')
    uid = models.CharField(max_length=20, db_index=True)
    access_token = models.CharField(max_length=500, blank=True, db_index=True)
    access_token_expires = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'uid'))