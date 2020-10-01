from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

from halemate_auth.models import User
from halemate_auth.serializers.user import UserUpdateSerializer
from halemate_auth.serializers.hospital import (
    HospitalSerializer,
    HospitalShortSerializer,
    HospitalViewSerializer,
)
from halemate_auth.permissions import (
    isVerified,
    NoPost,
    IsUserOrAdminOrReadOnly,
)


class HospitalViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(registered_as='H')
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsUserOrAdminOrReadOnly,
                          isVerified,
                          NoPost,
                          ]

    def list(self, request, *args, **kwargs):
        queryset = User.objects.filter(registered_as='H')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HospitalShortSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = HospitalShortSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        ser_data = serializer.data
        if instance.id == request.user.id:
            return Response(ser_data)
        else:
            ser_data.pop('hospital_appointments')
            return Response(ser_data)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = HospitalViewSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = UserUpdateSerializer
        return serializer_class
