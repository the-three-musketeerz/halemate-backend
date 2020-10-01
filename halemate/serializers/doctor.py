from rest_framework import serializers

from halemate_auth.serializers.hospital import HospitalShortSerializer
from halemate.models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    hospital = HospitalShortSerializer(many=True, read_only=True)

    def create(self, validated_data):
        validated_data['hospital'] = [self.context['request'].user, ]
        return super().create(validated_data)

    class Meta:
        model = Doctor
        fields = '__all__'
