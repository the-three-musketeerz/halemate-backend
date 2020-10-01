import hashlib
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.core.mail import send_mail

from halemate_auth.models import User, PasswordReset
from halemate_auth.permissions import isVerified
from halemate_auth.utils.generate_otp import generateOTP
from halemate_backend.settings import EMAIL_HOST_USER


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated, isVerified]

    def post(self, request, format=None):

        try:
            old_pass = request.data['old_password']
            new_pass = request.data['new_password']
            usr = request.user
            if usr.check_password(old_pass):
                usr.set_password(new_pass)
                usr.save()
                return Response(data={"detail": "password change successful"})
            else:
                return Response(data={"detail": "old password did not match"},
                                status=401)
        except:
            raise ParseError


class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):

        try:
            email = request.data['email']
            try:
                usr = User.objects.get(email=email)
                OTP = generateOTP()
                msg = f'Your OTP for password change is {OTP} .This OTP is ' \
                      f'valid for 10 minutes.'
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
            except User.DoesNotExist:
                return Response(data={"detail": "Email-id does not exist"},
                                status=409)
        except:
            raise ParseError


class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):

        try:
            email = request.data['email']
            OTP = request.data['OTP']
            new_password = request.data['new_password']
            usr = User.objects.get(email=email)
            OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
            pswrdrst = PasswordReset.objects.filter(user=usr).first()
            if pswrdrst.num_attempts > 0 and pswrdrst.expiry > timezone.now():
                if OTP_hash == pswrdrst.OTP:
                    usr.set_password(new_password)
                    usr.save()
                    pswrdrst.delete()
                    return Response(data={"detail": "success"}, status=200)
                else:
                    pswrdrst.num_attempts -= 1
                    pswrdrst.save()
                    if pswrdrst.num_attempts == 0:
                        pswrdrst.delete()
                        return Response(
                            data={"detail": "No. of invalid attempts exceeded",
                                  "num_attemps": 0}, status=409)
                    else:
                        return Response(
                            data={"detail": "Invalid OTP",
                                  "num_attempts": pswrdrst.num_attempts},
                            status=409)
            else:
                pswrdrst.delete()
                return Response(
                    data={"detail": "OTP Expired", "num_attempts": 0},
                    status=409)
        except:
            raise ParseError
