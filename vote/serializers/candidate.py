from rest_framework import serializers
from vote.models import candidate

class candidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidate
        fields = '__all__'
