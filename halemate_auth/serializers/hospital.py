from rest_framework import serializers

from halemate_auth.models import User
from halemate.serializers.short_serializers import DoctorShortSerializer


class HospitalShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phoneNumber']


class HospitalViewSerializer(serializers.ModelSerializer):
    doctors = DoctorShortSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'last_login', 'is_active', 'email',
                  'name', 'phoneNumber', 'registered_as',
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
