from halemate.models import *
from rest_framework import serializers

class AppointmentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class DoctorShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phoneNumber']

# only name and medical history field is editable
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'medical_history']
        read_only_fields = [id,]

class HospitalShortSerializer(serializers.ModelSerializer):
    # doctors = DoctorShortSerializer(many = True, read_only = True)
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phoneNumber']

class DoctorSerializer(serializers.ModelSerializer):

   # doctor_appointments = AppointmentShortSerializer(many = True, read_only = True)
    hospital = HospitalShortSerializer(many = True, read_only = True)

    def create(self, validated_data):
        validated_data['hospital'] = [self.context['request'].user,]
        return super().create(validated_data)

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
        read_only_fields = ['user', 'patient_name', 'hospital', 'doctor', 'reason']

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
        exclude = ['last_login', 'is_superuser', 'is_staff',
            'is_active', 'date_joined', 'groups', 'user_permissions'
        ]

class HospitalViewSerializer(serializers.ModelSerializer):
    doctors = DoctorShortSerializer(many = True, read_only = True)
    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_active', 'email', 
            'name', 'phoneNumber','registered_as', 
            'is_verified', 'hospital_appointments', 'doctors',
        ]

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