from django.contrib.auth.models import AbstractUser, UserManager


class CustomUser(AbstractUser):
    first_name = None
    last_name = None

    objects = UserManager()

    def __str__(self):
        return self.username
