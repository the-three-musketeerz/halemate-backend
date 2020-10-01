import requests
import json
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError

from rest_framework.response import Response
from rest_framework import permissions
from fcm_django.models import FCMDevice
from channels.layers import get_channel_layer

from halemate_auth.models import User
from halemate_backend.settings import SMS_AUTH
from halemate.utils.nearby_hospitals import searchNearbyHospitals
from halemate_auth.permissions import isVerified


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
