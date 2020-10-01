from django.contrib import admin
from halemate.models import Doctor, Appointment, TrustedContact

admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(TrustedContact)
