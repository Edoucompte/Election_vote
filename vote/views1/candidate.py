from vote.models import Candidate
from vote.serializers import CandidateSerializer
from rest_framework.views import APIView
from rest_framework import response, status
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from vote.views1.user import CustomAuthentication, res
from vote.paginations import CustomPaginator
from rest_framework.pagination import PageNumberPagination


class CandidateView(APIView):
    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(
        operation_description="Returns candidature list",
        responses= res
    )
    def get(self, request):

        if request.user.is_authenticated and  request.user.has_perm('vote.view_election'):
            candidates = Candidate.objects.all()
            paginator =PageNumberPagination()
            paginator_queryset = paginator.paginate_queryset(candidates, request)
            serializer = CandidateSerializer(paginator_queryset, many=True)
            # print("results", paginator.get_results(serializer.data))
            return response.Response({
                "data": CustomPaginator.format_json_response(paginator, serializer.data), # , serializer.data
                "details": "Liste des candidatures",
                "succes": True
            }, status=status.HTTP_200_OK)
            
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_description="Create new candidature",
        request_body=CandidateSerializer,
        responses= res
    )
    def post(self, request):
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CandidateDetailView(APIView):
    def get_object(self, pk):
        try:
            return Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_description="Returns a single candidate details",
        responses= res
    ) 
    def get(self, request, pk):
        candidate = self.get_object(pk)
        if not candidate:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CandidateSerializer(candidate)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Modify a single candidature details",
        request_body=CandidateSerializer,
        responses= res
    )    
    def put(self, request, pk):
        candidate = self.get_object(pk)
        if not candidate:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CandidateSerializer(candidate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Delete a single candidature by id",
        responses= {
            204:'no content',
            401: 'Unauthenticated',
            403: 'Access denied'
        }
    )
    def delete(self, request, pk):
        candidate= self.get_object(pk)
        if not candidate:
            return response.Response(
                {"error": "Candidature non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        candidate.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
