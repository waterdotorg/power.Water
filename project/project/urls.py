from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^project/', include('project.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^fbauth/', include('fbauth.urls')),
    (r'^twauth/', include('twauth.urls')),
    (r'', include('custom.urls')),
)
