from vote.models import Candidate
from vote.serializers import CandidateSerializer
from rest_framework.views import APIView
from rest_framework import response, status
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from vote.serializers.candidate import CandidateApprouveSerializer
from vote.views1.user import CustomAuthentication, res
from vote.paginations import CustomPaginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions


class CandidateView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [DjangoModelPermissions]

    @swagger_auto_schema(
        operation_description="Returns candidature list",
        responses= res
    )
    def get(self, request):

        if request.user.is_authenticated and  request.user.has_perm('vote.view_candidate'):
            if request.user.is_supervisor:
                candidates = Candidate.objects.all()
            else:
                candidates = Candidate.objects.filter(candidate_id= request.user.id) 
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
        if request.user.is_authenticated and  request.user.has_perm('vote.add_candidate'):
            serializer = CandidateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            return response.Response({
                "succes": False,
                "errors":serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

class CandidateDetailView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [DjangoModelPermissions]
    
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
        if request.user.is_authenticated and  request.user.has_perm('vote.view_candidate'):
            candidate = self.get_object(pk)
            if not candidate:
                return response.Response(
                    {
                        "succes": False,
                        "errors": "Candidature non trouvée"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = CandidateSerializer(candidate)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)


    @swagger_auto_schema(
        operation_description="Modify a single candidature details",
        request_body=CandidateSerializer,
        responses= res
    )    
    def put(self, request, pk):
        if request.user.is_authenticated and  request.user.has_perm('vote.change_candidate'):
            candidate = self.get_object(pk)
            if not candidate:
                return response.Response(
                    {
                        "succes": False,
                        "errors": "Candidature non trouvée"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = CandidateSerializer(candidate, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Delete a single candidature by id",
        responses= {
            204:'no content',
            401: 'Unauthenticated',
            403: 'Access denied'
        }
    )
    def delete(self, request, pk):
        if request.user.is_authenticated and  request.user.has_perm('vote.delete_candidate'):
            candidate= self.get_object(pk)
            if not candidate:
                return response.Response(
                    {"succes": False, "errors": "Candidature non trouvée"},
                    status=status.HTTP_404_NOT_FOUND
                )
            candidate.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

class CandidateApprouveView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [ DjangoModelPermissions] # only for supervisor or admin
    
    def get_object(self, pk):
        try:
            return Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            return None
    
    @swagger_auto_schema(
        operation_description="Modify a single candidature details",
        request_body=CandidateApprouveSerializer,
        responses= res
    )    
    def put(self, request, pk):
        if request.user.is_authenticated and  request.user.is_supervisor:
            candidate = self.get_object(pk)
            if not candidate:
                return response.Response(
                    { "succes": False, "error": "Candidature non trouvée"},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = CandidateApprouveSerializer(candidate, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)
    
class CandidatesListView(APIView):
    
    authentication_classes = [CustomAuthentication]
    permission_classes = [ DjangoModelPermissions] # only for supervisor or admin
    
    @swagger_auto_schema(
        operation_description="Returns approuved candidates list",
        responses= res
    )
    def get(self, request, election_id):
        '''
            Retourne la liste de scandidats a une election donee
        '''
        if request.user.is_authenticated and  request.user.is_active:
            candidates = Candidate.objects.filter(is_accepted= True, election_id= election_id) 
            paginator = PageNumberPagination()
            paginator_queryset = paginator.paginate_queryset(candidates, request)
            serializer = CandidateSerializer(paginator_queryset, many=True)
            # print("results", paginator.get_results(serializer.data))
            return response.Response({
                "data": CustomPaginator.format_json_response(paginator, serializer.data), # , serializer.data
                "details": "Liste des candidats",
                "succes": True
            }, status=status.HTTP_200_OK)
            
        return response.Response({
            "details": "Access denied",
            "succes": False,
        }, status=status.HTTP_403_FORBIDDEN)
