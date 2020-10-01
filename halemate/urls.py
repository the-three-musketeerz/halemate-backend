from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'doctor', views.DoctorViewSet)
router.register(
    r'appointment',
    views.AppointmentViewSet,
    basename='appointment'
)
router.register(
    r'trusted_contact',
    views.TrustedContactViewSet,
    basename='trusted_contact'
)

urlpatterns = [
    path(
        '',
        include(router.urls)
    ),
    path(
        'register_device/',
        views.RegisterDeviceView.as_view(),
        name='register_device'
    ),
    path(
        'alert/',
        views.AlertView.as_view(),
        name='alert'
    ),
    path(
        'report_alert/',
        views.ReportAlertView.as_view(),
        name='report_alert'),
]
