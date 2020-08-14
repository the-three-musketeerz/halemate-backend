from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from knox import views as knox_views

router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename = 'user')
router.register(r'hospital', views.HospitalViewSet, basename = 'hospital')
router.register(r'doctor', views.DoctorViewSet)
router.register(r'appointment', views.AppointmentViewSet, basename = 'appointment')
router.register(r'trusted_contact', views.TrustedContactViewSet, basename='trusted_contact')
router.register(r'whoami', views.WhoAmIViewSet, basename='whoami')

urlpatterns = [
    path('',include(router.urls)),
    path('signup/', views.SignupView.as_view(), name = 'signup'),
    path('login/',views.LoginView.as_view(), name='knox_login' ),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('change_password/', views.ChangePasswordView.as_view(), name = 'change_password'),
    path('register_device/', views.RegisterDeviceView.as_view(), name = 'register_device'),
    path('alert/', views.AlertView.as_view(), name = 'alert'),
    path('report_alert/', views.ReportAlertView.as_view(), name = 'report_alert'),
    path('forgot_password/', views.ForgotPasswordView.as_view(), name = 'forgot_password'),
    path('reset_password/', views.ResetPasswordView.as_view(), name = 'reset_password'),
    path('signup_verify/', views.SignupVerifyView.as_view(), name = 'signup_verify'),
    path('otp_verify/', views.OTPVerifyView.as_view(), name = 'otp_verify'),
    path('otp_refresh/', views.OTPRefreshView.as_view(), name = 'otp_refresh'),
]
