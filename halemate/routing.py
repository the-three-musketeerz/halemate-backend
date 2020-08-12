from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/halemate/<str:token>', consumers.NotificationConsumer),
]