from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import *
from .serializers import *
from django.contrib.auth import login
import requests
import json
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import permissions
from .permissions import *
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import status
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from fcm_django.models import FCMDevice
from django.core.mail import send_mail
from halemate_backend.settings import EMAIL_HOST_USER, SMS_AUTH
import math, random, hashlib
from django.utils import timezone
from datetime import timedelta

# Function to generate OTP
def generateOTP() : 
   
    string = '0123456789'
    OTP = "" 
    length = len(string) 
    for i in range(6) : 
        OTP += string[math.floor(random.random() * length)] 
  
    return OTP  

###############################################################

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(registered_as = 'U')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, isVerified, NoPost]

    def get_queryset(self):
        return User.objects.filter(id = self.request.user.id).filter(registered_as = 'U')

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = UserViewSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = UserUpdateSerializer
        return serializer_class

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(registered_as = 'H')
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrAdminOrReadOnly, isVerified, NoPost]

    def list(self, request, *args, **kwargs):
        queryset = User.objects.filter(registered_as = 'H')
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

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, hasDoctorPermission, isVerified]

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, hasAppointmentPermission, isVerified]

    def get_queryset(self):
        if self.request.user.registered_as == 'H':
            return Appointment.objects.filter(hospital = self.request.user)
        if self.request.user.registered_as == 'U':
            return Appointment.objects.filter(user = self.request.user)

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
                'type':200,
                'message':"New appointment",
                "appointment_id":str(serializer.data['id'])
            }
            room_group_name = 'hospital_'+str(serializer.data['hospital'])
            async_to_sync(layer.group_send)(
                room_group_name,
                {
                    'type': 'notify',
                    'message': json.dumps(message)
                }
            )
        except:
            pass
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TrustedContactViewSet(viewsets.ModelViewSet):
    serializer_class = TrustedContactSerializer
    permission_classes = [permissions.IsAuthenticated, isVerified, isUser]

    def get_queryset(self):
        return TrustedContact.objects.filter(user = self.request.user)

class WhoAmIViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ReadOnly, isVerified]

    def get_queryset(self):
        queryset = User.objects.filter(id = self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.request.user.registered_as == 'H':
            return HospitalViewSerializer
        elif self.request.user.registered_as == 'U':
            return UserViewSerializer

######################################################
# Authentication

class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)

class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format = None):

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
                u = User.objects.get(email = email)
                return Response(data = {"detail":"Email-id already exists"}, status = 400)
            except User.DoesNotExist:
                pass
            try:
                u = User.objects.get(phoneNumber = phoneNumber)
                return Response(data = {"detail":"Phone number already exists"}, status = 400)
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
            user_serializer = UserSerializer(data = user_obj)
            user_serializer.is_valid(raise_exception=True)
            user_data = user_serializer.data
            user = User.objects.create_user(
                email = user_data['email'],
                password = user_data['password'],
                name = user_data['name'],
                phoneNumber = user_data['phoneNumber'],
                registered_as = user_data['registered_as'],
                medical_history = user_data['medical_history'],
                is_verified = user_data['is_verified']
            )
            serializer = UserSerializer(user)
            return Response(data = serializer.data)

        except:
            raise ParseError

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated, isVerified]

    def post(self, request, format = None):

        try:
            old_pass = request.data['old_password']
            new_pass = request.data['new_password']
            usr = request.user
            if usr.check_password(old_pass):
                usr.set_password(new_pass)
                usr.save()
                return Response(data = {"detail":"password changed successfully"})
            else:
                return Response(data = {"detail":"old password did not match"}, status = 401)
        except:
            raise ParseError

class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format = None):

        try:
            email = request.data['email']
            try:
                usr = User.objects.get(email = email)
                OTP = generateOTP()
                msg = 'Your OTP for password change is '+OTP+' .This OTP is valid for 10 minutes.'
                send_mail(
                    'Halemate password change OTP',
                    msg,
                    EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )
                OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
                p = PasswordReset(user = usr, OTP = OTP_hash)
                p.save()
                return Response(data={"status":"OTP sent successfully","email":email}, status=200)
            except User.DoesNotExist:
                return Response(data={"detail":"Email-id does not exist"}, status=409)
        except:
            raise ParseError

class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format = None):

        try:
            email = request.data['email']
            OTP = request.data['OTP']
            new_password = request.data['new_password']
            usr = User.objects.get(email = email)
            OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
            pswrdrst = PasswordReset.objects.filter(user = usr).first()
            if pswrdrst.num_attempts > 0 and pswrdrst.expiry > timezone.now():
                if OTP_hash == pswrdrst.OTP:
                    usr.set_password(new_password)
                    usr.save()
                    pswrdrst.delete()
                    return Response(data={"detail":"success"}, status=200)
                else:
                    pswrdrst.num_attempts -= 1
                    pswrdrst.save()
                    if pswrdrst.num_attempts == 0:
                        return Response(data={"detail":"No. of invalid attempts exceeded","num_attemps":0}, status=409)
                        pswrdrst.delete()
                    else:
                        return Response(data={"detail":"Invalid OTP","num_attemps":pswrdrst.num_attempts}, status=409)
            else:
                return Response(data={"detail":"OTP Expired","num_attemps":0}, status=409)
                pswrdrst.delete()
        except:
            raise ParseError

class SignupVerifyView(APIView):
    permission_classes = [permissions.AllowAny,]

    def post(self, request, format = None):

        try:
            email = request.data['email']
            verification_method = request.data['verification_method']
            usr = User.objects.get(email = email)
            if usr.is_verified:
                return Response(data={"detail":"user already verified"}, status=400)
            OTP = generateOTP()
            msg = 'Your OTP for halemate verification is '+OTP+' .This OTP is valid for 10 minutes.'

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

                response = requests.request("GET", url, headers=headers, params=querystring)
                if response.status_code == 200:
                    OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
                    p = PasswordReset(user = usr, OTP = OTP_hash)
                    p.save()
                    return Response(data={"detail":"OTP sent successfully"}, status=200)
                else:
                    return Response(data={"detail":"Unable to send OTP"}, status=500)
                
            else:
                send_mail(
                    'Halemate password change OTP',
                    msg,
                    EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )
                OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
                p = PasswordReset(user = usr, OTP = OTP_hash)
                p.save()
                return Response(data={"status":"OTP sent successfully","email":email}, status=200)

        except:
            raise ParseError

class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny,]

    def post(self, request, format = None):
        try:
            email = request.data['email']
            usr = User.objects.get(email = email)
            if usr.is_verified:
                return Response(data={"detail":"user already verified"}, status=400)
            OTP = request.data['OTP']
            OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
            pswrdrst = PasswordReset.objects.filter(user = usr).first()
            if pswrdrst.num_attempts > 0 and pswrdrst.expiry > timezone.now():
                if OTP_hash == pswrdrst.OTP:
                    usr.is_verified = True
                    usr.save()
                    pswrdrst.delete()
                    return Response(data={"detail":"success"}, status=200)
                else:
                    pswrdrst.num_attempts -= 1
                    pswrdrst.save()
                    if pswrdrst.num_attempts == 0:
                        pswrdrst.delete()
                        usr.delete()
                        return Response(data={"detail":"No. of invalid attempts exceeded","num_attemps":0}, status=409)
                    else:
                        return Response(data={"detail":"Invalid OTP","num_attemps":pswrdrst.num_attempts}, status=409)
            else:
                pswrdrst.delete()
                usr.delete()
                return Response(data={"detail":"OTP Expired","num_attemps":0}, status=409)

        except:
            raise ParseError

class OTPRefreshView(APIView):
    permission_classes = [permissions.AllowAny,]
    def post(self, request, format = None):
        try:
            email = request.data['email']
            verification_method = request.data['verification_method']
            usr = User.objects.get(email = email)
            if usr.is_verified:
                return Response(data={"detail":"user already verified"}, status=400)
            p = PasswordReset.objects.filter(user = usr).first()
            if p:
                if p.num_attempts < 1:
                    usr.delete()
                    p.delete()
                    return Response(data={"detail":"too many wrong attempts"}, status=400)
                OTP = generateOTP()
                msg = 'Your OTP for halemate verification is '+OTP+' .This OTP is valid for 10 minutes.'
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

                    response = requests.request("GET", url, headers=headers, params=querystring)
                    if response.status_code == 200:
                        OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
                        p.OTP = OTP_hash
                        p.expiry = timezone.now() + timedelta(minutes=10)
                        p.save()
                        return Response(data={"detail":"OTP sent successfully"}, status=200)
                    else:
                        return Response(data={"detail":"Unable to send OTP"}, status=500)
                    
                else:
                    send_mail(
                        'Halemate password change OTP',
                        msg,
                        EMAIL_HOST_USER,
                        [email],
                        fail_silently=False
                    )
                    OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
                    p.OTP = OTP_hash
                    p.expiry = timezone.now() + timedelta(minutes=10)
                    p.save()
                    return Response(data={"status":"OTP sent successfully","email":email}, status=200)
            else:
                usr.delete()
                raise ParseError

        except:
            raise ParseError

##########################################################
# Alert + FCM

class RegisterDeviceView(APIView):
    permission_classes = [permissions.IsAuthenticated, isVerified]

    def post(self, request, format = None):

        try:
            registration_id = request.data['registration_id']
            device_type = 'android'
            user = request.user
            try:
                device_type = request.data['type']
            except:
                pass
            try:
                fcm_device = FCMDevice.objects.get(registration_id = registration_id)
                raise ParseError
            except:
                fcm_device = FCMDevice(registration_id = registration_id, user = user, type = device_type, active = True)
                fcm_device.save()
            return Response(data={"detail":"success"}, status=200)
        except:
            raise ParseError

class AlertView(APIView):
    permission_classes = [permissions.IsAuthenticated, isVerified]

    def post(self, request, format = None):

        try:
            location = request.data['location']
            user = request.user
            trusted = user.trusted_contacts.all()
            message = user.name + ' needs medical attention'
            for contact in trusted:
                try:
                    usr = User.objects.get(phoneNumber = contact.trusted_phone)
                    devices = FCMDevice.objects.filter(user = usr)
                    print(devices.registration_id)
                    devices.send_message(title='Medical Emergency', body = message)
                except:
                    pass

            contacts_tuple = tuple(map(lambda x:x.trusted_phone, trusted))
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

            response = requests.request("GET", url, headers=headers, params=querystring)
            print(response.status_code)
            
            try:
                layer = get_channel_layer()
                message = {
                    'type':505,
                    'message':"Medical Emergency",
                    "location":location,
                    "patient_name":user.name,
                    "patient_contact":user.phoneNumber
                }
                hospitals = User.objects.filter(registered_as = 'H')
                for hospital in hospitals:
                    room_group_name = 'hospital_'+str(hospital.id)
                    async_to_sync(layer.group_send)(
                        room_group_name,
                        {
                            'type': 'notify',
                            'message': json.dumps(message)
                        }
                    )
            except:
                pass
            return Response(data={"detail":"success"}, status=200)
        except:
            raise ParseError