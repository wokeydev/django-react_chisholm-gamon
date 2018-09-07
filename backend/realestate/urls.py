from .listings.api import ListingViewSet
from .alerts.api.views import PropertyAlertViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'properties', ListingViewSet, base_name='property')
router.register(r'alerts', PropertyAlertViewset, base_name='alert')


urlpatterns = router.urls
