from django.db import models

from employee.models import Employee


class Log(models.Model):
    employee = models.ForeignKey(Employee, models.DO_NOTHING, blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(null=True)

    class Meta:
        db_table = 'log'
