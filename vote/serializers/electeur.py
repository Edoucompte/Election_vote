from rest_framework import serializers
from vote.models import ProfilElecteur
from .user import CustomUserSerializer


class ProfilElecteurSerializer(serializers.ModelSerializer):
    #user = CustomUserSerializer()
    class Meta:
        model = ProfilElecteur
        fields = '__all__'

class ProfilElecteurGetSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    class Meta:
        model = ProfilElecteur
        fields = '__all__'