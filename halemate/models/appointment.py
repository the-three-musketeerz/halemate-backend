from django.db import models
from halemate_auth.models import User
from halemate.models import Doctor


class Appointment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        blank=True
    )
    patient_name = models.CharField(max_length=180)
    hospital = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hospital_appointments'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    reason = models.TextField(blank=True)
    appointment_made_time = models.DateTimeField(auto_now=True)
    appointment_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, default='P')

    class Meta:
        ordering = ['-appointment_made_time']