from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from log.api.v1.serializers.log import LogSerializer
from log.models import Log


class LogViewSet(ModelViewSet):
    serializer_class = LogSerializer
    queryset = Log.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = (
        'get',
        'delete',
    )
