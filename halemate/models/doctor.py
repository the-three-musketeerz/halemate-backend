from django.db import models
from halemate_auth.models import User


class Doctor(models.Model):
    name = models.CharField(max_length=180)
    hospital = models.ManyToManyField(User, related_name='doctors', blank=True)
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    specialization = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=15, unique=True)
