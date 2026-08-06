from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import response, status
from rest_framework.views import APIView

from vote.encryption import hashPassword
from vote.models import CustomUser, Invitation
from vote.serializers.invitation import InvitationAcceptSerializer, InvitationCreateSerializer, InvitationSerializer
from vote.views1.user import CustomAuthentication, res

INVITATION_STATUS_MESSAGES = {
    Invitation.STATUS_ACCEPTED: "Cette invitation a déjà été utilisée.",
    Invitation.STATUS_EXPIRED: "Cette invitation a expiré.",
    Invitation.STATUS_REVOKED: "Cette invitation a été révoquée.",
}


class InvitationView(APIView):
    """GET: list the connected supervisor's org invitations. POST: invite an email as supervisor."""

    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(operation_description="Liste des invitations de l'organisation", responses=res)
    def get(self, request):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        invitations = Invitation.objects.filter(organisation=request.user.organisation)
        serializer = InvitationSerializer(invitations, many=True)
        return response.Response({
            "succes": True,
            "details": "Liste des invitations",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Inviter un email à rejoindre l'organisation",
        request_body=InvitationCreateSerializer,
        responses=res,
    )
    def post(self, request):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        if not request.user.organisation_id:
            return response.Response(
                {"succes": False, "errors": "Aucune organisation associée à ce compte."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = InvitationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(
                {"succes": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email'].strip().lower()
        organisation = request.user.organisation

        if Invitation.objects.filter(
            organisation=organisation, email=email, status=Invitation.STATUS_PENDING
        ).exists():
            return response.Response(
                {"succes": False, "errors": "Une invitation est déjà en attente pour cet email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation = Invitation.objects.create(
            organisation=organisation,
            email=email,
            invited_by=request.user,
        )

        try:
            send_mail(
                "Super Vote - Invitation à rejoindre votre équipe",
                f"""
                    Bonjour,
                    {request.user.first_name} {request.user.last_name} vous invite à
                    rejoindre l'organisation "{organisation.name}" sur Super Vote
                    en tant que superviseur. Cliquez sur le lien suivant pour créer
                    votre compte (valide 7 jours) :
                    http://localhost:5173/invitations/{invitation.token}
                    Si vous ne vous attendiez pas à ce message, ignorez-le simplement.
                """,
                'super@vote.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print('Mail sending failed. Check the SMTP server:', e)

        out = InvitationSerializer(invitation)
        return response.Response({
            "succes": True,
            "details": "Invitation envoyée",
            "data": out.data,
        }, status=status.HTTP_201_CREATED)


class InvitationDetailView(APIView):
    """DELETE: revoke a pending invitation."""

    authentication_classes = [CustomAuthentication]

    def get_object(self, pk, organisation):
        try:
            # Org-scoped: never leak another org's invitation.
            return Invitation.objects.get(pk=pk, organisation=organisation)
        except Invitation.DoesNotExist:
            raise Http404

    @swagger_auto_schema(operation_description="Révoquer une invitation en attente", responses=res)
    def delete(self, request, pk):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        invitation = self.get_object(pk, request.user.organisation)
        if invitation.status != Invitation.STATUS_PENDING:
            return response.Response(
                {"succes": False, "errors": "Seule une invitation en attente peut être révoquée."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invitation.status = Invitation.STATUS_REVOKED
        invitation.save(update_fields=['status'])
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class InvitationAcceptView(APIView):
    """POST: public, the token is the auth. Creates the supervisor account in the invitation's org."""

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Accepter une invitation et créer son compte",
        request_body=InvitationAcceptSerializer,
        responses=res,
    )
    def post(self, request, token):
        try:
            invitation = Invitation.objects.select_related('organisation').get(token=token)
        except Invitation.DoesNotExist:
            return response.Response(
                {"succes": False, "errors": "Invitation introuvable."}, status=status.HTTP_404_NOT_FOUND
            )

        # Lazy expiry check: no need for a scheduled task to keep status accurate.
        if invitation.status == Invitation.STATUS_PENDING and invitation.is_expired():
            invitation.status = Invitation.STATUS_EXPIRED
            invitation.save(update_fields=['status'])

        if invitation.status != Invitation.STATUS_PENDING:
            return response.Response(
                {
                    "succes": False,
                    "errors": INVITATION_STATUS_MESSAGES.get(invitation.status, "Invitation invalide."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = InvitationAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(
                {"succes": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        data = serializer.validated_data

        if CustomUser.objects.filter(email=invitation.email).exists():
            return response.Response(
                {"succes": False, "errors": "Un compte existe déjà avec cet email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser(
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            email=invitation.email,
            organisation=invitation.organisation,
            is_supervisor=True,
            is_elector=False,
            is_candidate=False,
            is_staff=True,
            is_superuser=True,
        )
        try:
            validate_password(data['password'], user=user)
        except DjangoValidationError as e:
            return response.Response(
                {"succes": False, "errors": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user.password = hashPassword(data['password'])
            user.save()
            invitation.status = Invitation.STATUS_ACCEPTED
            invitation.save(update_fields=['status'])

        return response.Response(
            {
                "succes": True,
                "details": "Compte créé avec succès.",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "organisation": invitation.organisation_id,
                },
            },
            status=status.HTTP_201_CREATED,
        )
