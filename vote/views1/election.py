from rest_framework.views import APIView
from rest_framework import response, status
from vote.models import Election
from vote.serializers import ElectionSerializer
from django.http import Http404
from vote.permissions import IsSuperviseur

class ElectionView(APIView):
    permission_classes = [ IsSuperviseur ]
    def get(self, request, *args, **kwargs):
        elections = Election.objects.all()
        serializer = ElectionSerializer(elections, many=True)
        responserJson = {
            "data": serializer.data,
            "message": "Liste des elections",
            "error": False
        }
        
        return response.Response(responserJson, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ElectionSerializer(data=request.data)
        if(serializer.is_valid):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ElectionDetailView(APIView):
    permission_classes = [ IsSuperviseur ]
    def get_object(self, pk):
        try:
            return Election.objects.get(pk=pk)
        except Election.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        election = self.get_object(pk)
        serializer = ElectionSerializer(election)
        res = {
            "data": serializer.data,
            "message": f"Election id {pk}",
            "error": False
        }
        
        return response.Response(res, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        election = self.get_object(pk)
        serializer = ElectionSerializer(election, data=request.data, partial=True)
        if(serializer.is_valid):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        election = self.get_object(pk)
        election.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
