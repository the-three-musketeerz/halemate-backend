from rest_framework import permissions


class hasDoctorPermission(permissions.BasePermission):
    """
    Custom permission to allow only hospitals to post new doctors and allow only concerned hospital to edit the doctor
    """

    def has_permission(self, request, view):
        
        if request.method == 'POST' and request.user.registered_as != 'H':
            return False
        
        return True

    def has_object_permission(self, request, view, obj):

        if(request.user.registered_as == 'U'):
            return False

        if request.method in permissions.SAFE_METHODS and(request.user in obj.hospital.all()) :
            return True
        
        if (request.user.is_superuser):
            return True
        
        return False

class hasAppointmentPermission(permissions.BasePermission):
    """
    Custom permission to allow only the hospital to edit the appointment status and timing
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'DELETE' and (obj.status != 'P' and obj.status != 'R'):
            return False

        if request.user.registered_as == 'U':
            if request.method == 'DELETE':
                return True
            else:
                return False

        if (request.user.is_superuser) or (request.user == obj.hospital):
            return True

        return False
