# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Image.link'
        db.add_column('instagallery_image', 'link',
                      self.gf('django.db.models.fields.URLField')(default='http://water.org/', max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Image.link'
        db.delete_column('instagallery_image', 'link')


    models = {
        'instagallery.image': {
            'Meta': {'object_name': 'Image'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instagram_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['instagallery.Tag']"}),
            'thumbnail_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'instagallery.tag': {
            'Meta': {'object_name': 'Tag'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_processed_date': ('django.db.models.fields.DateTimeField', [], {}),
            'semaphore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['instagallery']