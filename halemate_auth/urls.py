from django.urls import path, include
from rest_framework.routers import DefaultRouter
from knox import views as knox_views

from halemate_auth.views.user import UserViewSet
from halemate_auth.views.hospital import HospitalViewSet
from halemate_auth.views.who_am_i import WhoAmIViewSet
from halemate_auth.views.login import LoginView
from halemate_auth.views.signup import SignupView, SignupVerifyView
from halemate_auth.views.password import (
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView
)
from halemate_auth.views.otp import OTPVerifyView, OTPRefreshView

app_name = 'halemate_auth'

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'hospital', HospitalViewSet, basename='hospital')
router.register(r'whoami', WhoAmIViewSet, basename='whoami')

urlpatterns = [
    path(
        '',
        include(router.urls)
    ),
    path(
        'signup/',
        SignupView.as_view(),
        name='signup'
    ),
    path(
        'login/',
        LoginView.as_view(),
        name='knox_login'
    ),
    path(
        'logout/',
        knox_views.LogoutView.as_view(),
        name='knox_logout'
    ),
    path(
        'change_password/',
        ChangePasswordView.as_view(),
        name='change_password'
    ),
    path(
        'forgot_password/',
        ForgotPasswordView.as_view(),
        name='forgot_password'),
    path(
        'reset_password/',
        ResetPasswordView.as_view(),
        name='reset_password'),
    path(
        'signup_verify/',
        SignupVerifyView.as_view(),
        name='signup_verify'),
    path(
        'otp_verify/',
        OTPVerifyView.as_view(),
        name='otp_verify'
    ),
    path(
        'otp_refresh/',
        OTPRefreshView.as_view(),
        name='otp_refresh'
    ),
]
