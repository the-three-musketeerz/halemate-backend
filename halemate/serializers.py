from halemate.models import *
from rest_framework import serializers

class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser',
            'is_staff', 'is_active', 'email', 
            'name', 'phoneNumber', 'medical_history',
            'registered_as', 'is_verified', 'appointments',
            'trusted_contacts',
        ]

class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['registered_as'] = 'U'
        return super().create(validated_data)

    class Meta:
        model = User
        fields = '__all__'

class HospitalViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser',
            'is_staff', 'is_active', 'email', 
            'name', 'phoneNumber','registered_as', 
            'is_verified', 'hospital_appointments', 'doctors',
        ]

class HospitalSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['registered_as'] = 'H'
        return super().create(validated_data)

    class Meta:
        model = User
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):

    doctor_appointments = AppointmentSerializer(many = True, read_only = True)
    class Meta:
        model = Doctor
        fields = '__all__'

class TrustedContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedContact
        fields = '__all__'