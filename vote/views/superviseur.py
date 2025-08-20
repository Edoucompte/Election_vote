from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import ProfilSuperviseur
from vote.serializers import ProfilSuperviseurSerializer

class ProfilSuperviseurModelViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilSuperviseurSerializer
    queryset = ProfilSuperviseur.objects.all()
