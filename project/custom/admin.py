from django.contrib import admin

from custom.models import Profile, Post, TwitterStatusUpdate, FacebookStatusUpdate, FacebookStatusUpdateLog, \
    FacebookOGReferredLog, TwitterAutoFriendshipLog, TwitterStatusUpdateLog

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'followers', 'user_referrer', 'source_referrer', 'social_data_completed']
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

class TwitterStatusUpdateLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'twitter_status_update', 'created_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'twitter_status_update__content']
    ordering = ['-created_date']

class TwitterAutoFriendshipLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'success', 'created_date']
    ordering = ['-created_date']

class FacebookStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['name', 'link', 'caption', 'start_date', 'end_date', 'created_date']
    search_fields = ['link', 'name', 'caption', 'description']
    ordering = ['-created_date']
    filter_horizontal = ('groups',)

class FacebookStatusUpdateLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'facebook_status_update', 'created_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'facebook_status_update__name']
    ordering = ['-created_date']

class FacebookOGReferredLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_referred', 'success', 'created_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user_referred__username',
        'user_referred__first_name', 'user_referred__last_name']
    ordering = ['-created_date']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(TwitterStatusUpdate, TwitterStatusUpdateAdmin)
admin.site.register(TwitterStatusUpdateLog, TwitterStatusUpdateLogAdmin)
admin.site.register(TwitterAutoFriendshipLog, TwitterAutoFriendshipLogAdmin)
admin.site.register(FacebookStatusUpdate, FacebookStatusUpdateAdmin)
admin.site.register(FacebookStatusUpdateLog, FacebookStatusUpdateLogAdmin)
admin.site.register(FacebookOGReferredLog, FacebookOGReferredLogAdmin)