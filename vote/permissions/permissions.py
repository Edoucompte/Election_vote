from rest_framework import permissions


class IsSupervisor(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_supervisor:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.supervisor == request.user:
            return True
        return False
             
class IsSupervisorElection(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET' :
         return True # tout le monde peut voir
        return request.user.is_authenticated and request.user.is_elector
    
def has_object_permission(self, request, view, obj):
        if request.user.is_supervisor and obj.user == request.user:
            return True
        return False