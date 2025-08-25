from rest_framework import serializers
from vote.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        #fields = ['id', 'first_name', 'last_name', 'email', 'sexe', 'date_joined', 'date_naissance', 'matricule', 'is_active', 'is_staff']
        exclude = ('password', "groups", 'user_permissions')