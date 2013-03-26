from django.db import models

class Tag(models.Model):
    tag = models.CharField(max_length=256, help_text="Recent media tag")
    semaphore = models.BooleanField(default=False)
    last_processed_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s" % self.tag

class Image(models.Model):
    tag = models.ForeignKey(Tag)
    instagram_id = models.CharField(max_length=256, db_index=True)
    link = models.URLField()
    thumbnail_url = models.URLField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s" % self.thumbnail_url