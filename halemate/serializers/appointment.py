from rest_framework import serializers

from halemate_auth.serializers.hospital import HospitalShortSerializer
from halemate_auth.serializers.user import UserShortSerializer
from halemate.models import Appointment
from halemate.serializers.short_serializers import DoctorShortSerializer


class AppointmentViewSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    hospital = HospitalShortSerializer(read_only=True)
    doctor = DoctorShortSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        if self.context['request'].user.registered_as == 'H':
            validated_data['hospital'] = self.context['request'].user
        else:
            validated_data['status'] = 'P'
            validated_data['appointment_time'] = None
        return super().create(validated_data)

    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['user', 'patient_name', 'hospital', 'doctor',
                            'reason']
