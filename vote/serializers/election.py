from rest_framework import serializers
from vote.models import Election

class ElectionSerializer(serializers.ModelSerializer):
    #supervisor = serializers.IntegerField(read_only=True)
    class Meta:
        model = Election
        fields = '__all__'
