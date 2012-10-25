from django.conf.urls import patterns, url

urlpatterns = patterns('custom.views',
    url(r'^ajax/email-form/$', 'ajax_email_form', name='ajax_email_form'),
    url(r'^ajax/settings-form/$', 'ajax_settings_form', name='ajax_settings_form'),
    url(r'^post/(?P<slug>[-\w]+)/$', 'post', name='post'),
    url(r'^signout/$', 'signout', name='signout'),
    url(r'^$', 'homepage', name='homepage'),
)