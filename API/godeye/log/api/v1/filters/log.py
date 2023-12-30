from django.db.models.functions import Concat
from django.db.models import Value
from django_filters import rest_framework as filters

from log.models import Log


class LogFilter(filters.FilterSet):
    keyword = filters.CharFilter(method="search_by_name")
    dates = filters.Filter(method="search_by_dates")

    class Meta:
        model = Log
        fields = ("keyword", "dates")

    def search_by_name(self, queryset, name, value):
        queryset = queryset.annotate(
            fullname=Concat("employee__first_name", Value(" "), "employee__last_name")
        )
        return queryset.filter(fullname__icontains=value)

    def search_by_dates(self, queryset, name, value):
        return queryset.filter(last_seen__range=value)
