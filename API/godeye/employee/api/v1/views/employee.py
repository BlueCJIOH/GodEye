import datetime

from django.db.models import Count, Min, F, Max
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ModelViewSet

from employee.api.v1.filters.employee import EmployeeFilter
from employee.api.v1.serializers.employee import (
    EmployeeSerializer,
    EmployeeFilterSerializer,
    EmployeeStatsSerializer,
)
from employee.models import Employee


class EmployeeViewSet(ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = (AllowAny,)
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
    def search_employee(self, request):
        serializer = EmployeeFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.get_queryset()
        filterset = EmployeeFilter(data=serializer.data)
        filterset.is_valid()
        queryset = filterset.filter_queryset(queryset=queryset)
        data = EmployeeSerializer(queryset, many=True).data
        return Response(data)

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="stats",
    )
    def get_employee_stats(self, request):
        try:
            queryset = (
                self.get_queryset()
                .filter(
                    id=request.data["id"],
                    log__last_seen__range=(
                        request.data.get(
                            "date_from",
                            datetime.datetime.now().replace(
                                hour=0, minute=0, second=0, microsecond=0
                            ),
                        ),
                        request.data.get("date_to", datetime.datetime.now()),
                    ),
                )
                .values("log__last_seen__date")
                .annotate(
                    total_visits=Count("log"),
                    first_seen=Min("log__last_seen"),
                    last_seen=Max("log__last_seen"),
                )
                .values("total_visits", "first_seen", "last_seen")
            )
            return Response(
                EmployeeStatsSerializer(queryset, many=True).data, status=HTTP_200_OK
            )
        except Exception:
            return Response(status=HTTP_404_NOT_FOUND)
