from django.conf.urls import patterns, include, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.APIRootView.as_view()),
    url(r'^locks/$', views.LockListView.as_view(), name='lock-list'),
    url(r'^locks/(?P<resource_name>\w{1,64})/$',
        views.LockDetailView.as_view(), name='lock-detail'),
    url(r'^locks/(?P<resource_name>\w{1,64})/owner/$',
        views.OwnerDetailView.as_view(), name='lock-owner'),
    url(r'^locks/(?P<resource_name>\w{1,64})/requests/$',
        views.RequestListView.as_view(), name='lock-requests'),
    url(r'^locks/(?P<resource_name>\w{1,64})/requests/(?P<pk>\w+)/$',
        views.RequestDetailView.as_view(), name='request-detail'),
)
