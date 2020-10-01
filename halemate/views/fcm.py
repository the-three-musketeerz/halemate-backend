from rest_framework.views import APIView
from rest_framework.exceptions import ParseError

from rest_framework.response import Response
from rest_framework import permissions
from fcm_django.models import FCMDevice
from halemate_auth.permissions import isVerified


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
