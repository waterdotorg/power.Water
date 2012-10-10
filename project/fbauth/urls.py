from django.conf.urls import patterns, include, url

urlpatterns = patterns('fbauth.views',
    url(r'^fbauth/$', 'fbauth', name='fbauth'),
)