from django.contrib import admin

from twauth.models import TwitterUser

class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'uid', 'created']
    search_fields = ('uid',)
    ordering = ('-created',)

admin.site.register(TwitterUser, TwitterUserAdmin)