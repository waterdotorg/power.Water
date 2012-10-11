from django.conf.urls import patterns, url

urlpatterns = patterns('twauth.views',
    url(r'^twauth/$', 'twauth', name='twauth'),
)