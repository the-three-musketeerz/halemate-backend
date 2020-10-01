from rest_framework import viewsets
from rest_framework import permissions

from halemate_auth.models import User
from halemate_auth.serializers.user import UserViewSerializer
from halemate_auth.serializers.hospital import HospitalViewSerializer
from halemate_auth.permissions import isVerified, ReadOnly


class WhoAmIViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ReadOnly, isVerified]

    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.request.user.registered_as == 'H':
            return HospitalViewSerializer
        elif self.request.user.registered_as == 'U':
            return UserViewSerializer
