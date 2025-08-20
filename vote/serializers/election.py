from rest_framework import serializers
from vote.models import Election

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = '__all__'
