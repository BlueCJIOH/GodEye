from rest_framework import routers

from employee.api.v1.views.employee import EmployeeViewSet

router = routers.SimpleRouter()
router.register("employee", EmployeeViewSet, basename="employee")

urlpatterns = router.urls
