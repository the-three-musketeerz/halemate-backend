import json
from asgiref.sync import async_to_sync
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer

from halemate.models import Appointment
from halemate.serializers.appointment import (
    AppointmentViewSerializer,
    AppointmentUpdateSerializer,
    AppointmentSerializer
)
from halemate.permissions import hasAppointmentPermission
from halemate_auth.permissions import isVerified


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated,
                          hasAppointmentPermission, isVerified]

    def get_queryset(self):
        if self.request.user.registered_as == 'H':
            return Appointment.objects.filter(hospital=self.request.user)
        if self.request.user.registered_as == 'U':
            return Appointment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = AppointmentViewSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = AppointmentUpdateSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        try:
            layer = get_channel_layer()
            message = {
                'type': 200,
                'message': "New appointment",
                "appointment_id": str(serializer.data['id'])
            }
            room_group_name = 'hospital_' + str(serializer.data['hospital'])
            async_to_sync(layer.group_send)(
                room_group_name,
                {
                    'type': 'notify',
                    'message': json.dumps(message)
                }
            )
        except:
            pass
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
