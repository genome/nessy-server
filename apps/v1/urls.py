from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'claims', views.ClaimViewSet)

urlpatterns = router.urls
