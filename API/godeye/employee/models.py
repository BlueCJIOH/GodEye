from django.db import models


class Employee(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    img_path = models.CharField(max_length=255, blank=True, null=True)
    encoded_img = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = 'employee'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
