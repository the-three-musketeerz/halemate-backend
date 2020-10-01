from rest_framework import serializers

from halemate.models import Appointment, Doctor


class AppointmentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class DoctorShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
