from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import Candidature, CustomUser, Election, ProfilElecteur, ProfilSuperviseur, Vote
from vote.serializers import CandidatureSerializer, CustomUserSerializer, ElectionSerializer, ProfilElecteurSerializer, ProfilSuperviseurSerializer, VoteSerializer

# Create your views here.
class CustomUserModelViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

class ProfilElecteurModelViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilElecteurSerializer
    queryset = ProfilElecteur.objects.all()

class ProfilSuperviseurModelViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilSuperviseurSerializer
    queryset = ProfilSuperviseur.objects.all()

class ElectionModelViewSet(viewsets.ModelViewSet):
    serializer_class = ElectionSerializer
    queryset = Election.objects.all()

class VoteModelViewSet(viewsets.ModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()

class CandidatureModelViewSet(viewsets.ModelViewSet):
    serializer_class = CandidatureSerializer
    queryset = Candidature.objects.all()
