from django.contrib import admin

from custom.models import Profile, Post, TwitterStatusUpdate

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'followers', 'user_referrer', 'source_referrer', 'type', 'social_data_completed']
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'source_referrer')
    ordering = ['-user__date_joined']

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title',  'homepage', 'published_date', 'created_date']
    search_fields = ('title', 'content')
    ordering = ['-created_date']

class TwitterStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['content', 'link', 'start_date', 'end_date', 'created_date']
    search_fields = ['content','link']
    ordering = ['-created_date']
    filter_horizontal = ('groups',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(TwitterStatusUpdate, TwitterStatusUpdateAdmin)