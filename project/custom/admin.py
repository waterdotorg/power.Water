from django.contrib import admin

from custom.models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'followers', 'user_referrer', 'source_referrer', 'type', 'social_data_completed']
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'source_referrer')
    ordering = ['-user__date_joined']

admin.site.register(Profile, ProfileAdmin)