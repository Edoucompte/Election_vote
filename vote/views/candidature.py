from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import Candidature
from vote.serializers import CandidatureSerializer


class CandidatureModelViewSet(viewsets.ModelViewSet):
    serializer_class = CandidatureSerializer
    queryset = Candidature.objects.all()
