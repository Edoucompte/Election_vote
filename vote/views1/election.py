from rest_framework.views import APIView
from rest_framework import response, status
from vote.models import Election
from vote.serializers import ElectionSerializer
from django.http import Http404
from vote.permissions import IsSupervisor
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from vote.views1.user import res

class ElectionView(APIView):
    permission_classes = [ IsSupervisor ]
    
    @swagger_auto_schema(
        operation_description="Returns elections list",
        responses= res
    )
    def get(self, request, *args, **kwargs):
        elections = Election.objects.all()
        serializer = ElectionSerializer(elections, many=True)
        responserJson = {
            "data": serializer.data,
            "message": "Liste des elections",
            "error": False
        }
        
        return response.Response(responserJson, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create new election",
        request_body=ElectionSerializer,
        responses= res
    )
    def post(self, request):
        serializer = ElectionSerializer(data=request.data)
        if(serializer.is_valid):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ElectionDetailView(APIView):
    permission_classes = [ IsSupervisor ]
    def get_object(self, pk):
        try:
            return Election.objects.get(pk=pk)
        except Election.DoesNotExist:
            raise Http404
       
    @swagger_auto_schema(
        operation_description="Returns a single election details",
        responses= res
    ) 
    def get(self, request, pk):
        election = self.get_object(pk)
        serializer = ElectionSerializer(election)
        res = {
            "data": serializer.data,
            "message": f"Election id {pk}",
            "error": False
        }
        
        return response.Response(res, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Modify a single election details",
        request_body=ElectionSerializer,
        responses= res
    )
    def put(self, request, pk, *args, **kwargs):
        election = self.get_object(pk)
        serializer = ElectionSerializer(election, data=request.data, partial=True)
        if(serializer.is_valid):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Delete a single election by id",
        responses= {
            204:'no content',
            401: 'Unauthenticated',
            403: 'Access denied'
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        election = self.get_object(pk)
        election.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
