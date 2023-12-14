from django.db.models.functions import Concat
from django.db.models import Value
from django_filters import rest_framework as filters

from employee.models import Employee


class EmployeeFilter(filters.FilterSet):
    keyword = filters.CharFilter(method='search_employee')

    class Meta:
        model = Employee
        fields = ('keyword',)

    def search_employee(self, queryset, name, value):
        queryset = queryset.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        return queryset.filter(fullname__icontains=value)
