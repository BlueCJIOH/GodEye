from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from log.api.v1.filters.log import LogFilter
from log.api.v1.serializers.log import LogSerializer, LogFilterSerializer
from log.models import Log


class LogViewSet(ModelViewSet):
    serializer_class = LogSerializer
    queryset = Log.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = (
        'get',
        'delete',
        'post',
    )

    @action(detail=False, methods=['post', ], url_path='search')
    def search_log(self, request):
        serializer = LogFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.get_queryset()
        filterset = LogFilter(data=serializer.data)
        filterset.is_valid()
        queryset = filterset.filter_queryset(queryset=queryset)
        data = LogSerializer(queryset, many=True).data
        return Response(data)
