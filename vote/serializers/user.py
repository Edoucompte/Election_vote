from rest_framework import serializers
from vote.encryption import hashPassword
from vote.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        #fields = ['id', 'first_name', 'last_name', 'email', 'sexe', 'date_joined', 'date_naissance', 'matricule', 'is_active', 'is_staff']
        exclude = ( "groups", 'user_permissions')

        def create(self, validated_data):
            password = validated_data.pop('password')
            user = CustomUser(**validated_data)
            user['password'] = hashPassword(password) #.set_password(password)
            user.save()
            return user