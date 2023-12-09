from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from employee.api.v1.serializers.employee import EmployeeSerializer
from employee.models import Employee


class EmployeeViewSet(ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = (
        'get',
        'delete',
    )
