from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from vote.models import Election
from vote.serializers import ElectionSerializer


class ElectionModelViewSet(viewsets.ModelViewSet):
    serializer_class = ElectionSerializer
    queryset = Election.objects.all()
