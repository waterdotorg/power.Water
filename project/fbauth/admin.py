from django.contrib import admin

from fbauth.models import FacebookUser

class FacebookUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'uid', 'status', 'created']
    search_fields = ('uid',)
    ordering = ('-created',)

admin.site.register(FacebookUser, FacebookUserAdmin)