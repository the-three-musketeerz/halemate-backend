from rest_framework import serializers

from halemate_auth.models import User


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phoneNumber']


# only name and medical history field is editable
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'medical_history']
        read_only_fields = [id, ]


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
