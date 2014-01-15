from django.conf.urls import patterns, include, url
from apps.v1 import views as views_v1


urlpatterns = patterns('',
    url(r'^v1/$', views_v1.APIRootView.as_view()),
    url(r'^v1/locks/$', views_v1.LockListView.as_view(), name='lock-list'),
    url(r'^v1/locks/(?P<resource_name>\w{1,64})/$',
        views_v1.LockDetailView.as_view()),
    url(r'^v1/locks/(?P<resource_name>\w{1,64})/owner/$',
        views_v1.OwnerDetailView.as_view()),
    url(r'^v1/locks/(?P<resource_name>\w{1,64})/requests/$',
        views_v1.RequestListView.as_view()),
    url(r'^v1/locks/(?P<resource_name>\w{1,64})/requests/(?P<pk>\w+)/$',
        views_v1.RequestDetailView.as_view()),
)
