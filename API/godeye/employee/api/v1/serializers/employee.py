import logging
import pickle

import numpy
from PIL import Image
import face_recognition
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from employee.models import Employee


class EmployeeSerializer(ModelSerializer):
    encoded_img = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_encoded_img(self, obj):
        return pickle.loads(obj.encoded_img)


class EmployeeFilterSerializer(serializers.Serializer):
    keyword = serializers.CharField()


class EmployeeStatsSerializer(serializers.Serializer):
    total_visits = serializers.IntegerField()
    first_seen = serializers.DateTimeField()
    last_seen = serializers.DateTimeField()


class EmployeeCreateSerializer(ModelSerializer):
    name = serializers.CharField(required=False)
    img = serializers.FileField()

    class Meta:
        model = Employee
        fields = (
            "id",
            "first_name",
            "last_name",
            "img_path",
            "encoded_img",
            "name",
            "img",
        )
        read_only_fields = ("id", "first_name", "last_name", "img_path", "encoded_img")

    def create(self, validated_data):
        try:
            file_name, file_type = validated_data["img"].name.split(".")
            first_name, last_name = validated_data.get("name", file_name).split()
            img_path = default_storage.save(
                f'{" ".join((first_name, last_name))}.{file_type}',
                validated_data.get("img"),
            )
            encoded_img = pickle.dumps(face_recognition.face_encodings(numpy.array(Image.open(f'media/{img_path}')))[0])
            instance = Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                img_path=img_path,
                encoded_img=encoded_img,
            )
            return EmployeeSerializer(
                instance=instance
            ).data
        except Exception as err:
            logging.critical(err)
