import datetime

from django.db import models
from django.db.models import Count, F, Case, When, Value, Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from log.api.v1.filters.log import LogFilter
from log.api.v1.serializers.log import (
    LogSerializer,
    LogFilterSerializer,
    LogStatsSerializer,
)
from log.models import Log


class LogViewSet(ModelViewSet):
    serializer_class = LogSerializer
    queryset = Log.objects.all()
    permission_classes = (IsAuthenticated,)
    http_method_names = (
        "get",
        "delete",
        "post",
    )

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="search",
    )
    def search_log(self, request):
        serializer = LogFilterSerializer(data=request.data)
        serializer.is_valid(rdaise_exception=True)
        queryset = self.get_queryset()
        filterset = LogFilter(data=serializer.data)
        filterset.is_valid()
        queryset = filterset.filter_queryset(queryset=queryset)
        data = LogSerializer(queryset, many=True).data
        return Response(data)

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="stats",
    )
    def get_log_stats(self, request):
        queryset = (
            self.get_queryset().filter(
                employee_id__isnull=True,
                last_seen__range=(
                    request.data.get(
                        "date_from",
                        datetime.datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ),
                    ),
                    request.data.get("date_to", datetime.datetime.now()),
                ),
            )
            if request.data.get("select_empls") is False
            else self.get_queryset().filter(
                last_seen__range=(
                    request.data.get(
                        "date_from",
                        datetime.datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ),
                    ),
                    request.data.get("date_to", datetime.datetime.now()),
                )
            )
        )
        queryset = (
            queryset.values("last_seen__date")
            .annotate(
                select_empls=Value(
                    request.data.get("select_empls", None),
                    output_field=models.BooleanField(),
                )
            )
            .annotate(
                total_detected=Case(
                    When(
                        Q(select_empls=False) | Q(select_empls__isnull=True),
                        then=Count("*"),
                    ),
                    When(select_empls=True, then=Count("employee_id")),
                ),
                date=F("last_seen__date"),
            )
        ).values("total_detected", "date")
        return Response(
            LogStatsSerializer(queryset, many=True).data,
            status=HTTP_200_OK,
        )
