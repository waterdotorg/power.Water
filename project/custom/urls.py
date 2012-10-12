from django.conf.urls import patterns, url

urlpatterns = patterns('custom.views',
    url(r'^post/(?P<slug>[-\w]+)/$', 'post', name='post'),
    url(r'^signout/$', 'signout', name='signout'),
    url(r'^$', 'homepage', name='homepage'),
)