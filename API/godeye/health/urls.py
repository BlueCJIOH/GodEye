from rest_framework import routers

from health.api.v1.views.health import HealthViewSet

router = routers.SimpleRouter()
router.register("health", HealthViewSet, basename="Health")
urlpatterns = router.urls
