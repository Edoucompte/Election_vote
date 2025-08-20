from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import CustomUser
from vote.serializers import CustomUserSerializer

# Create your views here.
class CustomUserModelViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
