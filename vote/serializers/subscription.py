from rest_framework import serializers

from vote.models import Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'price_cents', 'currency',
            'max_elections', 'max_electors', 'max_candidatures_per_election',
            'is_active',
        ]
