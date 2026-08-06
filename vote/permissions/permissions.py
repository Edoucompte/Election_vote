from rest_framework import permissions


class IsSupervisor(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_supervisor:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # obj peut être une Election (obj.organisation) ou un objet lié via
        # obj.election.organisation (Candidate, Vote...). Un superviseur ne doit
        # jamais avoir la main sur les données d'une autre organisation, même
        # s'il n'en est pas explicitement le "supervisor" du champ.
        organisation = getattr(obj, 'organisation_id', None)
        if organisation is None:
            organisation = getattr(getattr(obj, 'election', None), 'organisation_id', None)
        return (
            request.user.organisation_id is not None
            and organisation == request.user.organisation_id
        )

class IsSupervisorElection(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method == 'GET' :
         return True # tout le monde peut voir
        return request.user.is_authenticated and request.user.is_elector

    def has_object_permission(self, request, view, obj):
        organisation = getattr(obj, 'organisation_id', None)
        return (
            request.user.is_authenticated
            and request.user.organisation_id is not None
            and organisation == request.user.organisation_id
        )