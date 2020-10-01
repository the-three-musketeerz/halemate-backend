from datetime import timedelta
from django.utils import timezone
from django.db import models

from halemate_auth.models import User


def get_expiry():
    return timezone.now() + timedelta(minutes=10)


class PasswordReset(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    OTP = models.CharField(max_length=256)
    num_attempts = models.IntegerField(default=3)
    expiry = models.DateTimeField(default=get_expiry)

    class Meta:
        ordering = ['-expiry']
