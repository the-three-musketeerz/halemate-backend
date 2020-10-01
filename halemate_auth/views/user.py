from rest_framework import viewsets
from rest_framework import permissions

from halemate_auth.models import User
from halemate_auth.serializers.user import (
    UserSerializer,
    UserViewSerializer,
    UserUpdateSerializer,
)
from halemate_auth.permissions import (
    isVerified,
    NoPost,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(registered_as='U')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, isVerified, NoPost]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id).\
            filter(registered_as='U')

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'GET':
            serializer_class = UserViewSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            serializer_class = UserUpdateSerializer
        return serializer_class
