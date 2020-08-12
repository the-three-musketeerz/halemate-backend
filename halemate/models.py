from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):

    # choice to register as user or hospital
    USER = 'U'
    HOSPITAL = 'H'
    register_choices = [(USER, 'User'), (HOSPITAL, 'Hospital')]

    first_name = None
    last_name = None
    username = None
    email = models.EmailField(unique = True)
    name = models.CharField(max_length = 180)
    phoneNumber = models.CharField(max_length = 15, unique = True)
    medical_history = models.TextField(blank = True)
    registered_as = models.CharField(
        max_length = 1, 
        choices = register_choices, 
        default = USER
        )
    is_verified = models.BooleanField(default = False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Doctor(models.Model):
    name = models.CharField(max_length = 180)
    hospital = models.ManyToManyField(User, related_name = 'doctors', blank = True)
    time_start = models.TimeField(null = True)
    time_end = models.TimeField(null = True)
    specialization = models.CharField(max_length = 100)
    phoneNumber = models.CharField(max_length = 15, unique = True)


class Appointment(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete = models.CASCADE, 
        related_name='appointments',
        blank = True
        )
    patient_name = models.CharField(max_length = 180)
    hospital = models.ForeignKey(
        User, 
        on_delete = models.CASCADE, 
        related_name='hospital_appointments'
        )
    doctor = models.ForeignKey(
        Doctor,
        on_delete = models.CASCADE,
        related_name = 'doctor_appointments'
    )
    reason = models.TextField(blank = True)
    appointment_made_time = models.DateTimeField(auto_now = True)
    appointment_time = models.DateTimeField(null = True)
    status = models.CharField(max_length = 20, default = 'P')

class TrustedContact(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete = models.CASCADE, 
        related_name='trusted_contacts'
        )
    trusted_name = models.CharField(max_length = 180)
    trusted_phone = models.CharField(max_length = 15, unique = True)