from django.conf.urls import patterns, include, url
from . import views

_RESOURCE_NAME = '(?P<resource_name>[A-Za-z0-9:_-]{1,64})'

urlpatterns = patterns('',
    url(r'^$', views.APIRootView.as_view()),
    url(r'^locks/$', views.LockListView.as_view(), name='lock-list'),
    url(r'^locks/' + _RESOURCE_NAME + '/$',
        views.LockDetailView.as_view(), name='lock-detail'),
    url(r'^locks/' + _RESOURCE_NAME + '/owner/$',
        views.OwnerDetailView.as_view(), name='lock-owner'),
    url(r'^locks/' + _RESOURCE_NAME + '/requests/$',
        views.RequestListView.as_view(), name='lock-requests'),
    url(r'^requests/$',
        views.RequestListView.as_view(), name='request-list'),
    url(r'^requests/(?P<pk>\w+)/$',
        views.RequestDetailView.as_view(), name='request-detail'),
)
