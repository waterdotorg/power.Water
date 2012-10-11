from django.conf.urls import patterns, url

urlpatterns = patterns('custom.views',
    url(r'^signout/$', 'signout', name='signout'),
    url(r'^$', 'homepage', name='homepage'),
)