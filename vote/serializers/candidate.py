from rest_framework import serializers
from vote.models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    reject_message = serializers.CharField(read_only=True)
    class Meta:
        model = Candidate
        fields = '__all__'

class CandidateApprouveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['status', 'reject_message']
