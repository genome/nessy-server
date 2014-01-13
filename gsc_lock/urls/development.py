from django.conf.urls import patterns, include, url
from django.contrib import admin

from gsc_lock.urls.common import urlpatterns

admin.autodiscover()

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
