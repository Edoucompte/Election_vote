from rest_framework import permissions


class IsSuperviseur(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_supervise:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.superviseur == request.user:
            return True
        return False