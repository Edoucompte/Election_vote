from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import Vote
from vote.serializers import VoteSerializer


class VoteModelViewSet(viewsets.ModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()
