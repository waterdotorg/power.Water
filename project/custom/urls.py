from django.conf.urls import patterns, url

urlpatterns = patterns('custom.views',
    url(r'^ajax/email-form/$', 'ajax_email_form', name='ajax_email_form'),
    url(r'^ajax/settings-form/$', 'ajax_settings_form', name='ajax_settings_form'),
    url(r'^signout/$', 'signout', name='signout'),
    url(r'^signin/$', 'signin', name='signin'),
    url(r'^post/(?P<post_slug>[-\w]+)/$', 'homepage', name='homepage'),
    url(r'^opt-in/(?P<hex_digi>[-\w]+)/$', 'hex_digi', name='hex_digi'),
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^$', 'homepage', name='homepage'),
)
