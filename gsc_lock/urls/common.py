from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'v1/', include('apps.v1.urls')),
)
