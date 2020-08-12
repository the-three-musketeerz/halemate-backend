from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from knox.auth import TokenAuthentication
from rest_framework import exceptions, HTTP_HEADER_ENCODING

class NotificationConsumer(WebsocketConsumer):
    def connect(self):

        self.token = self.scope['url_route']['kwargs']['token']

        knoxAuth = TokenAuthentication()
        user, auth_token = knoxAuth.authenticate_credentials(self.token.encode(HTTP_HEADER_ENCODING))

        if user:

            self.room_group_name = 'hospital_'+str(user.id)
            self.user = user
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )       
            self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        pass

    def notify(self, event):
         message = event['message']
         self.send(text_data=message)