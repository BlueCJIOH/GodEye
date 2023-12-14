from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from employee.api.v1.filters.employee import EmployeeFilter
from employee.api.v1.serializers.employee import EmployeeSerializer, EmployeeFilterSerializer
from employee.models import Employee


class EmployeeViewSet(ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = (
        'get',
        'delete',
        'post',
    )

    @action(detail=False, methods=['post', ], url_path='search')
    def search_employee(self, request):
        serializer = EmployeeFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.get_queryset()
        filterset = EmployeeFilter(data=serializer.data)
        filterset.is_valid()
        queryset = filterset.filter_queryset(queryset=queryset)
        data = EmployeeSerializer(queryset, many=True).data
        return Response(data)
