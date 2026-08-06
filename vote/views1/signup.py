from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import response, status
from rest_framework.views import APIView

from vote.encryption import hashPassword
from vote.models import CustomUser, Organisation
from vote.serializers.signup import SignupSerializer

res = {
    201: "Compte créé",
    400: "Requête invalide",
}


class SignupView(APIView):
    """POST: dedicated signup. Creates a supervisor + new org in one transaction,
    with a usable password right away (unlike CustomUserView.post's minimal
    bootstrap, which defers password setup to the emailed link)."""

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Créer un compte superviseur et sa nouvelle organisation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
                "organisation_name": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["first_name", "last_name", "email", "password", "organisation_name"],
        ),
        responses=res,
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(
                {"succes": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        email = data['email'].strip().lower()

        # Generic error: don't leak whether the existing account is a supervisor or elector.
        if CustomUser.objects.filter(email=email).exists():
            return response.Response(
                {"succes": False, "errors": "Un compte existe déjà avec cet email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organisation_name = data['organisation_name'].strip()
        if not organisation_name:
            return response.Response(
                {"succes": False, "errors": "Le nom de l'organisation est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Unsaved instance so validate_password can check it against
        # UserAttributeSimilarityValidator, same as ResetUserPasswordView.
        user = CustomUser(
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            email=email,
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
            organisation = Organisation.objects.create(name=organisation_name)
            user.organisation = organisation
            user.password = hashPassword(data['password'])
            user.save()
            organisation.owner = user
            organisation.save(update_fields=['owner'])

        return response.Response(
            {
                "succes": True,
                "details": "Compte créé avec succès.",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "organisation": organisation.id,
                    "organisation_name": organisation.name,
                },
            },
            status=status.HTTP_201_CREATED,
        )
