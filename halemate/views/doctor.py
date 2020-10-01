from rest_framework import viewsets
from rest_framework import permissions

from halemate.models import Doctor
from halemate.serializers.doctor import DoctorSerializer
from halemate.permissions import hasDoctorPermission
from halemate_auth.permissions import isVerified


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, hasDoctorPermission,
                          isVerified]
