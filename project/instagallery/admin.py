from django.contrib import admin
from instagallery.models import Tag, Image

class TagAdmin(admin.ModelAdmin):
    list_display = ['tag', 'last_processed_date', 'created_date']
    search_fields = ('tag',)
    ordering = ['-created_date']

class ImageAdmin(admin.ModelAdmin):
    list_display = ['tag', 'instagram_id', 'thumbnail_url', 'created_date']
    search_fields = ('tag__tag', 'instagram_id', 'thumbnail_url')
    ordering = ['-created_date']

admin.site.register(Tag, TagAdmin)
admin.site.register(Image, ImageAdmin)