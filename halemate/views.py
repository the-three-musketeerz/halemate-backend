from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import *
from .serializers import *
from django.contrib.auth import login

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.exceptions import ParseError
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(registered_as = 'U')
    serializer_class = UserSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = UserViewSerializer
        return serializer_class

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(registered_as = 'H')
    serializer_class = HospitalSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = HospitalViewSerializer
        return serializer_class

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = AppointmentViewSerializer
        return serializer_class

class TrustedContactViewSet(viewsets.ModelViewSet):
    queryset = TrustedContact.objects.all()
    serializer_class = TrustedContactSerializer

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
                medical_history = user_data['medical_history']
            )
            serializer = UserSerializer(user)
            return Response(data = serializer.data)

        except:
            raise ParseError