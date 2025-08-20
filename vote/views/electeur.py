from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import ProfilElecteur
from vote.serializers import ProfilElecteurSerializer

class ProfilElecteurModelViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilElecteurSerializer
    queryset = ProfilElecteur.objects.all()
