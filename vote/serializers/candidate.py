from rest_framework import serializers
from vote.models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    is_accepted = serializers.BooleanField(read_only=True)
    reject_message = serializers.CharField(read_only=True)
    class Meta:
        model = Candidate
        fields = '__all__'

class CandidateApprouveSerializer(serializers.Serializer):
    is_accepted = serializers.BooleanField()
    reject_message = serializers.CharField()
