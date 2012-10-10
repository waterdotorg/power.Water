from django.conf.urls import patterns, include, url

urlpatterns = patterns('custom.views',
    url(r'^$', 'homepage', name='homepage'),
)