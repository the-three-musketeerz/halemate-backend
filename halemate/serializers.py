from halemate.models import *
from rest_framework import serializers

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phoneNumber']

class HospitalShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phoneNumber']

class AppointmentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class DoctorShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):

    doctor_appointments = AppointmentShortSerializer(many = True, read_only = True)
    hospital = HospitalShortSerializer(many = True, read_only = True)
    class Meta:
        model = Doctor
        fields = '__all__'

class AppointmentViewSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only = True)
    hospital = HospitalShortSerializer(read_only = True)
    doctor = DoctorShortSerializer(read_only = True)
    class Meta:
        model = Appointment
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Appointment
        fields = '__all__'

class UserViewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser',
            'is_staff', 'is_active', 'email', 
            'name', 'phoneNumber', 'medical_history',
            'registered_as', 'is_verified', 'appointments',
            'trusted_contacts',
        ]
        depth = 1

class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['registered_as'] = 'U'
        return super().create(validated_data)

    class Meta:
        model = User
        exclude = ['last_login', 'is_superuser', 'is_staff',
            'is_active', 'date_joined', 'groups', 'user_permissions'
        ]

class HospitalViewSerializer(serializers.ModelSerializer):
    hospital_appointments = AppointmentSerializer(many = True, read_only = True)
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_superuser',
            'is_staff', 'is_active', 'email', 
            'name', 'phoneNumber','registered_as', 
            'is_verified', 'hospital_appointments', 'doctors',
        ]
        depth = 1

class HospitalSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['registered_as'] = 'H'
        return super().create(validated_data)

    class Meta:
        model = User
        exclude = ['last_login', 'is_superuser', 'is_staff',
            'is_active', 'date_joined', 'groups', 'user_permissions',
            'medical_history'
        ]


class TrustedContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedContact
        fields = '__all__'