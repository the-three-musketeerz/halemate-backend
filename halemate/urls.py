from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from knox import views as knox_views

router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename = 'user')
router.register(r'hospital', views.HospitalViewSet, basename = 'hospital')
router.register(r'doctor', views.DoctorViewSet)
router.register(r'appointment', views.AppointmentViewSet)
router.register(r'trusted_contact', views.TrustedContactViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('signup/', views.SignupView.as_view(), name = 'signup'),
    path('login/',views.LoginView.as_view(), name='knox_login' ),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
]
