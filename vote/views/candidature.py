from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import Candidate
from vote.serializers import CandidateSerializer


class CandidatureModelViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateSerializer
    queryset = Candidate.objects.all()
