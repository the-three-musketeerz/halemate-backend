from rest_framework import serializers

from halemate.models import TrustedContact


class TrustedContactSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = TrustedContact
        fields = '__all__'
