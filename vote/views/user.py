from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from vote.filters.users import UserFilter
from vote.models import CustomUser
from vote.serializers import CustomUserSerializer

# Create your views here.
class CustomUserModelViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter ]
    #filterset_class = UserFilter
    filter_fields = ( 'is_active', 'is_superviseur', 'sexe')
    search_fields = ('first_name', 'last_name', 'email')
    ordering_fields = ('+first_name', )
