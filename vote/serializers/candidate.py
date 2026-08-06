from rest_framework import serializers
from vote.models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    reject_message = serializers.CharField(read_only=True)
    class Meta:
        model = Candidate
        fields = '__all__'


class PublicCandidateSerializer(serializers.ModelSerializer):
    """Candidate list a voter sees: no raw FK id resolution needed on the front."""
    candidate_name = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = ['id', 'election', 'candidate', 'candidate_name', 'description']

    def get_candidate_name(self, obj):
        return f"{obj.candidate.first_name} {obj.candidate.last_name}".strip()

class CandidateApprouveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['status', 'reject_message']
