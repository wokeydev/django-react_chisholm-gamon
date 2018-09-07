from rest_framework import permissions


class AlertPermissions(permissions.BasePermission):
    """
    Alert's API permissions. If they are logged in, they see their own.
    Otherwise Post only.
    """

    def has_permission(self, request, view):
        if request.method == "POST" or request.user.pk:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        elif request.user.email_address == obj.email:
            return True
        return False
