import hashlib
import requests
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.core.mail import send_mail

from halemate_auth.models import User, PasswordReset
from halemate_auth.serializers.user import UserSerializer
from halemate_auth.utils.generate_otp import generateOTP
from halemate_backend.settings import EMAIL_HOST_USER, SMS_AUTH


class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):

        try:
            email = request.data['email']
            password = request.data['password']
            name = request.data['name']
            phoneNumber = request.data['phoneNumber']
            registered_as = request.data['registered_as']
            medical_history = ''
            is_verified = False
            try:
                medical_history = request.data['medical_history']
            except:
                pass
            try:
                u = User.objects.get(email=email)
                return Response(data={"detail": "Email-id already exists"},
                                status=400)
            except User.DoesNotExist:
                pass
            try:
                u = User.objects.get(phoneNumber=phoneNumber)
                return Response(data={"detail": "Phone number already exists"},
                                status=400)
            except User.DoesNotExist:
                pass
            user_obj = {
                'email': email,
                'password': password,
                'name': name,
                'phoneNumber': phoneNumber,
                'registered_as': registered_as,
                'medical_history': medical_history,
                'is_verified': is_verified
            }
            user_serializer = UserSerializer(data=user_obj)
            user_serializer.is_valid(raise_exception=True)
            user_data = user_serializer.data
            user = User.objects.create_user(
                email=user_data['email'],
                password=user_data['password'],
                name=user_data['name'],
                phoneNumber=user_data['phoneNumber'],
                registered_as=user_data['registered_as'],
                medical_history=user_data['medical_history'],
                is_verified=user_data['is_verified']
            )
            serializer = UserSerializer(user)
            return Response(data=serializer.data)

        except:
            raise ParseError


class SignupVerifyView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None):

        try:
            email = request.data['email']
            verification_method = request.data['verification_method']
            usr = User.objects.get(email=email)
            if usr.is_verified:
                return Response(data={"detail": "user already verified"},
                                status=400)
            OTP = generateOTP()
            msg = f'Your OTP for halemate verification is {OTP} .This OTP is' \
                  f' valid for 10 minutes.'

            if verification_method == 'M':
                phone = usr.phoneNumber
                url = "https://www.fast2sms.com/dev/bulk"
                querystring = {
                    "authorization": SMS_AUTH,
                    "sender_id": "FSTSMS",
                    "message": msg,
                    "language": "english",
                    "route": "p",
                    "numbers": phone,
                }

                headers = {"cache-control": "no-cache"}

                response = requests.request("GET", url, headers=headers,
                                            params=querystring)
                if response.status_code == 200:
                    OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
                    p = PasswordReset(user=usr, OTP=OTP_hash)
                    p.save()
                    return Response(data={"detail": "OTP sent successfully"},
                                    status=200)
                else:
                    return Response(data={"detail": "Unable to send OTP"},
                                    status=500)

            else:
                send_mail(
                    'Halemate password change OTP',
                    msg,
                    EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )
                OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
                p = PasswordReset(user=usr, OTP=OTP_hash)
                p.save()
                return Response(
                    data={"status": "OTP sent successfully", "email": email},
                    status=200)

        except:
            raise ParseError
