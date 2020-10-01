from django.db import models
from halemate_auth.models import User


class TrustedContact(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trusted_contacts',
        blank=True
    )
    trusted_name = models.CharField(max_length=180)
    trusted_phone = models.CharField(max_length=15)

    class Meta:
        unique_together = ('user', 'trusted_phone')