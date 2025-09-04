from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication
from vote.filters.users import UserFilter
from vote.models import CustomUser
from vote.serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class CustomUserModelViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter ]
    #filterset_class = UserFilter
    filter_fields = ( 'is_active', 'is_supervisor', 'sex')
    search_fields = ('first_name', 'last_name', 'email')
    ordering_fields = ('first_name', )
   # authentication_classes = [SessionAuthentication]
   # permission_classes = [IsAuthenticated]
