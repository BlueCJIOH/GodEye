import pickle

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from employee.models import Employee


class EmployeeSerializer(ModelSerializer):
    encoded_img = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_encoded_img(self, obj):
        return pickle.loads(obj.encoded_img)
