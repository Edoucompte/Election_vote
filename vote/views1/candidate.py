

from vote.models import candidate
from vote.serializers import candidateSerializer
from rest_framework.views import APIView
from rest_framework import response, status
from django.http import Http404


class candidateView(APIView):

    def get(self, request):
        candidate = candidate.objects.all()
        serializer = candidateSerializer(candidate, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = candidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class candidateDetailView(APIView):
    def get_object(self, pk):
        try:
            return candidate.objects.get(pk=pk)
        except candidate.DoesNotExist:
            return None

    def get(self, request, pk):
        candidate = self.get_object(pk)
        if not candidate:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = candidateSerializer(candidate)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        candidate = self.get_object(pk)
        if not candidate:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = candidateSerializer(candidate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        candidate= self.get_object(pk)
        if not candidate:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        candidate.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
