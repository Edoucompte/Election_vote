from rest_framework import serializers
from vote.models import Candidature

class CandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = '__all__'
