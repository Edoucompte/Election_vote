from rest_framework import serializers
from vote.models import ProfilSuperviseur

class ProfilSuperviseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilSuperviseur
        fields = '__all__'