from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from halemate.models import TrustedContact
from halemate.serializers.trusted_contact import TrustedContactSerializer
from halemate_auth.permissions import isVerified, isUser


class TrustedContactViewSet(viewsets.ModelViewSet):
    serializer_class = TrustedContactSerializer
    permission_classes = [permissions.IsAuthenticated, isVerified, isUser]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super().create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return TrustedContact.objects.filter(user=self.request.user)
