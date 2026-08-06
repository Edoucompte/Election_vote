from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    """Payload for POST /auth/signup/ : creates a supervisor + their organisation."""

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    organisation_name = serializers.CharField(max_length=150)
