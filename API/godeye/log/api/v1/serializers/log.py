import datetime

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from log.models import Log


class LogSerializer(ModelSerializer):
    employee = serializers.SlugRelatedField(slug_field="first_name", read_only=True)

    class Meta:
        model = Log
        fields = "__all__"


class LogFilterSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False)
    dates = serializers.ListField(required=False)
    employee = serializers.SlugRelatedField(slug_field="first_name", read_only=True)

    def validate_dates(self, value):
        if len(value) == 1:
            value.append(datetime.datetime.now())
        return value


class LogStatsSerializer(serializers.Serializer):
    total_detected = serializers.IntegerField()
    date = serializers.DateField()
