from django.urls import path, include
from rest_framework.routers import DefaultRouter
from halemate.views.alert import AlertView, ReportAlertView
from halemate.views.appointment import AppointmentViewSet
from halemate.views.doctor import DoctorViewSet
from halemate.views.fcm import RegisterDeviceView
from halemate.views.trusted_contact import TrustedContactViewSet

router = DefaultRouter()
router.register(r'doctor', DoctorViewSet)
router.register(
    r'appointment',
    AppointmentViewSet,
    basename='appointment'
)
router.register(
    r'trusted_contact',
    TrustedContactViewSet,
    basename='trusted_contact'
)

urlpatterns = [
    path(
        '',
        include(router.urls)
    ),
    path(
        'register_device/',
        RegisterDeviceView.as_view(),
        name='register_device'
    ),
    path(
        'alert/',
        AlertView.as_view(),
        name='alert'
    ),
    path(
        'report_alert/',
        ReportAlertView.as_view(),
        name='report_alert'),
]
