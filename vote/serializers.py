from rest_framework import serializers
from vote.models import Candidature, CustomUser, Election, ProfilElecteur, ProfilSuperviseur, Vote

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'sexe', 'date_joined', 'date_naissance', 'matricule', 'is_active', 'is_staff']

class ProfilElecteurSerializer(serializers.ModelSerializer):
    #user = CustomUserSerializer()
    class Meta:
        model = ProfilElecteur
        fields = '__all__'

class ProfilSuperviseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilSuperviseur
        fields = '__all__'

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = '__all__'

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'

class CandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = '__all__'
