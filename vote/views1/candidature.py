

from vote.models import Candidature
from vote.serializers import CandidatureSerializer
from rest_framework.views import APIView
from rest_framework import response, status
from django.http import Http404


class CandidatureView(APIView):

    def get(self, request):
        candidatures = Candidature.objects.all()
        serializer = CandidatureSerializer(candidatures, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CandidatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CandidatureDetailView(APIView):
    def get_object(self, pk):
        try:
            return Candidature.objects.get(pk=pk)
        except Candidature.DoesNotExist:
            return None

    def get(self, request, pk):
        candidature = self.get_object(pk)
        if not candidature:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CandidatureSerializer(candidature)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        candidature = self.get_object(pk)
        if not candidature:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CandidatureSerializer(candidature, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        candidature = self.get_object(pk)
        if not candidature:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        candidature.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
