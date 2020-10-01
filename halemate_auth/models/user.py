from django.contrib.auth.models import AbstractUser
from django.db import models

from halemate_auth.managers import user


class User(AbstractUser):

    # choice to register as user or hospital
    USER = 'U'
    HOSPITAL = 'H'
    register_choices = [(USER, 'User'), (HOSPITAL, 'Hospital')]

    first_name = None
    last_name = None
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=180)
    phoneNumber = models.CharField(max_length=15, unique=True)
    medical_history = models.TextField(blank=True)
    registered_as = models.CharField(
        max_length=1,
        choices=register_choices,
        default=USER
        )
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = user.UserManager()

    def __str__(self):
        return self.email
