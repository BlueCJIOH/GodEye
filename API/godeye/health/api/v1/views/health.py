from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from health.api.v1.services.health import check_db_health, check_redis_health


class HealthViewSet(GenericViewSet):
    @extend_schema(request=None, responses=None)
    @action(methods=["get"], detail=False, url_path="web")
    def get_health(self, request):
        return Response(data={"db": check_db_health(), "redis": check_redis_health()})

    @action(methods=["post"], detail=False, url_path="reboot")
    def reboot(self, request):
        pass
