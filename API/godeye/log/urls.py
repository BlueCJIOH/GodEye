from rest_framework import routers
from log.api.v1.views.log import LogViewSet

router = routers.SimpleRouter()
router.register("log", LogViewSet, basename="log")

urlpatterns = router.urls
