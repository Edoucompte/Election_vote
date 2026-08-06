from rest_framework import serializers

from vote.models import Invitation


class InvitationCreateSerializer(serializers.Serializer):
    """Payload for POST /organisations/invitations/ : email to invite."""

    email = serializers.EmailField()


class InvitationSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True, default=None)

    class Meta:
        model = Invitation
        fields = ['id', 'email', 'status', 'created_at', 'expires_at', 'invited_by_email']
        read_only_fields = fields


class InvitationAcceptSerializer(serializers.Serializer):
    """Payload for POST /organisations/invitations/<token>/accept/."""

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
