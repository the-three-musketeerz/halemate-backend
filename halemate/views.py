import requests
import json
from asgiref.sync import async_to_sync
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from fcm_django.models import FCMDevice
from channels.layers import get_channel_layer

from halemate.models import Doctor, Appointment, TrustedContact
from halemate_auth.models import User
from halemate.serializers.doctor import DoctorSerializer
from halemate.serializers.appointment import (
    AppointmentViewSerializer,
    AppointmentUpdateSerializer,
    AppointmentSerializer
)
from halemate.serializers.trusted_contact import TrustedContactSerializer
from halemate.permissions import hasAppointmentPermission, hasDoctorPermission
from halemate_backend.settings import SMS_AUTH
from halemate.nearby_hospitals import searchNearbyHospitals
from halemate_auth.permissions import isVerified, isUser


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, hasDoctorPermission,
                          isVerified]


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


class TrustedContactViewSet(viewsets.ModelViewSet):
    serializer_class = TrustedContactSerializer
    permission_classes = [permissions.IsAuthenticated, isVerified, isUser]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super().create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return TrustedContact.objects.filter(user=self.request.user)


##########################################################
# Alert + FCM

class RegisterDeviceView(APIView):
    permission_classes = [permissions.IsAuthenticated, isVerified]

    def post(self, request, format=None):

        try:
            registration_id = request.data['registration_id']
            device_type = 'android'
            user = request.user
            try:
                device_type = request.data['type']
            except:
                pass
            try:
                fcm_device = FCMDevice.objects.get(
                    registration_id=registration_id)
                raise ParseError
            except:
                fcm_device = FCMDevice(registration_id=registration_id,
                                       user=user, type=device_type,
                                       active=True)
                fcm_device.save()
            return Response(data={"detail": "success"}, status=200)
        except:
            raise ParseError


class AlertView(APIView):
    permission_classes = [permissions.IsAuthenticated, isVerified]

    def post(self, request, format=None):

        try:
            lat = request.data['lat']
            lng = request.data['lng']
            user = request.user
            trusted = user.trusted_contacts.all()
            message = user.name + ' needs medical attention'
            for contact in trusted:
                try:
                    usr = User.objects.get(phoneNumber=contact.trusted_phone)
                    devices = FCMDevice.objects.filter(user=usr)
                    print(devices.registration_id)
                    devices.send_message(title='Medical Emergency',
                                         body=message)
                except:
                    continue

            contacts_tuple = tuple(map(lambda x: x.trusted_phone, trusted))
            contacts_string = ",".join(contacts_tuple)

            url = "https://www.fast2sms.com/dev/bulk"
            querystring = {
                "authorization": SMS_AUTH,
                "sender_id": "FSTSMS",
                "message": message,
                "language": "english",
                "route": "p",
                "numbers": contacts_string,
            }

            headers = {"cache-control": "no-cache"}

            response = requests.request("GET", url, headers=headers,
                                        params=querystring)
            print(response.status_code)

            try:
                layer = get_channel_layer()
                message = {
                    'type': 505,
                    'message': "Medical Emergency",
                    "lat": lat,
                    "lng": lng,
                    "patient_name": user.name,
                    "patient_contact": user.phoneNumber
                }
                hospitals = User.objects.filter(registered_as='H')
                for hospital in hospitals:
                    room_group_name = 'hospital_' + str(hospital.id)
                    async_to_sync(layer.group_send)(
                        room_group_name,
                        {
                            'type': 'notify',
                            'message': json.dumps(message)
                        }
                    )
            except:
                pass
            return Response(data={"detail": "success"}, status=200)
        except:
            raise ParseError


class ReportAlertView(APIView):
    permission_classes = [permissions.IsAuthenticated, isVerified]

    def post(self, request, format=None):

        try:
            lat = request.data['lat']
            lng = request.data['lng']
            hospitals = searchNearbyHospitals(lat, lng)
            return Response(data=hospitals)
        except:
            raise ParseError
