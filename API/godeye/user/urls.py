from rest_framework import routers
from log.api.v1.views.log import LogViewSet

router = routers.SimpleRouter()
router.register("user", LogViewSet, basename="user")

urlpatterns = router.urls
