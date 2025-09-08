from rest_framework import permissions


class IsSupervisor (permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_supervisor:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.supervisor == request.user:
            return True
        return False 