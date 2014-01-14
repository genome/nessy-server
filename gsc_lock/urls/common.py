from django.conf.urls import patterns, include, url
from apps.v1 import views as views_v1
from rest_framework import routers

router_v1 = routers.DefaultRouter()
router_v1.register(r'locks', views_v1.LockViewSet, base_name='Lock')
router_v1.register(r'resources', views_v1.ResourceViewSet, base_name='Resource')


urlpatterns = patterns('',
    url(r'^v1/', include(router_v1.urls)),
)
