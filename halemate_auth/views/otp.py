import hashlib
import requests
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.core.mail import send_mail

from halemate_auth.models import User, PasswordReset
from halemate_auth.utils.generate_otp import generateOTP
from halemate_backend.settings import EMAIL_HOST_USER, SMS_AUTH


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None):
        try:
            email = request.data['email']
            usr = User.objects.get(email=email)
            if usr.is_verified:
                return Response(data={"detail": "user already verified"},
                                status=400)
            OTP = request.data['OTP']
            OTP_hash = hashlib.sha256(OTP.encode()).hexdigest()
            pswrdrst = PasswordReset.objects.filter(user=usr).first()
            if pswrdrst.num_attempts > 0 and pswrdrst.expiry > timezone.now():
                if OTP_hash == pswrdrst.OTP:
                    usr.is_verified = True
                    usr.save()
                    pswrdrst.delete()
                    return Response(data={"detail": "success"}, status=200)
                else:
                    pswrdrst.num_attempts -= 1
                    pswrdrst.save()
                    if pswrdrst.num_attempts == 0:
                        pswrdrst.delete()
                        usr.delete()
                        return Response(
                            data={"detail": "No. of invalid attempts exceeded",
                                  "num_attempts": 0},
                            status=409)
                    else:
                        return Response(
                            data={"detail": "Invalid OTP",
                                  "num_attempts": pswrdrst.num_attempts},
                            status=409)
            else:
                pswrdrst.delete()
                usr.delete()
                return Response(
                    data={"detail": "OTP Expired", "num_attempts": 0},
                    status=409)

        except:
            raise ParseError


class OTPRefreshView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None):
        try:
            email = request.data['email']
            verification_method = request.data['verification_method']
            usr = User.objects.get(email=email)
            if usr.is_verified:
                return Response(data={"detail": "user already verified"},
                                status=400)
            p = PasswordReset.objects.filter(user=usr).first()
            if p:
                if p.num_attempts < 1:
                    usr.delete()
                    p.delete()
                    return Response(data={"detail": "too many wrong attempts"},
                                    status=400)
                OTP = generateOTP()
                msg = f'Your OTP for halemate verification is {OTP} .' \
                      f'This OTP is valid for 10 minutes.'
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
                        p.OTP = OTP_hash
                        p.expiry = timezone.now() + timedelta(minutes=10)
                        p.save()
                        return Response(
                            data={"detail": "OTP sent successfully"},
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
                    p.OTP = OTP_hash
                    p.expiry = timezone.now() + timedelta(minutes=10)
                    p.save()
                    return Response(data={"status": "OTP sent successfully",
                                          "email": email}, status=200)
            else:
                usr.delete()
                raise ParseError

        except:
            raise ParseError