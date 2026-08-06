from rest_framework.views import APIView
from rest_framework import response, status
from vote.models import Election
from vote.serializers import ElectionSerializer
from django.http import Http404
from vote.permissions import IsSupervisor
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from vote.views1.user import CustomAuthentication, res
from vote.paginations import CustomPaginator
from rest_framework.pagination import PageNumberPagination

class ElectionView(APIView):
    # permission_classes = [ IsSupervisor ]
    authentication_classes = [CustomAuthentication]
    
    @swagger_auto_schema(
        operation_description="Returns elections list",
        responses= res
    )
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and  request.user.has_perm('vote.view_election'):
            elections = Election.objects.select_related('supervisor').prefetch_related('electors', 'candidates').filter(
                organisation=request.user.organisation
            )
            # paginator =PageNumberPagination()
            # paginator_queryset = paginator.paginate_queryset(elections, request)
            serializer = ElectionSerializer(elections, many=True)
            # print("results", paginator.get_results(serializer.data))
            return response.Response({
                "data": serializer.data, #CustomPaginator.format_json_response(paginator, serializer.data), # , 
                "details": "Liste des elections",
                "succes": True
            }, status=status.HTTP_200_OK)
            
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

    
    @swagger_auto_schema(
        operation_description="Create new election",
        request_body=openapi.Schema(
            description="Request body for election creation",
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="name"),
                'begin_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="begin date timestamp"),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="end date timestamp"),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description="description"),
                # 'state': openapi.Schema(type=openapi.TYPE_STRING, description="state"),
            },
        ),
        responses= res
    )
    def post(self, request):
        #print("request in post election view", request.data.keys())
        if request.user.is_authenticated and  request.user.has_perm('vote.add_election'):
            if not request.user.organisation_id:
                return response.Response({
                    "details": "Vous devez appartenir à une organisation pour créer une élection.",
                    "succes": False
                }, status=status.HTTP_400_BAD_REQUEST)
            # organisation/supervisor sont read-only sur le serializer : ils sont
            # fixés ici depuis l'utilisateur connecté, jamais depuis le corps envoyé.
            serializer = ElectionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(supervisor=request.user, organisation=request.user.organisation)
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)


class ElectionDetailView(APIView):
    authentication_classes = [CustomAuthentication]
    # permission_classes = [ IsSupervisor ]
    def get_object(self, pk, organisation):
        try:
            # Filtrer par organisation ici est ce qui empêche un superviseur
            # d'une organisation de voir/modifier/supprimer l'élection d'une
            # autre organisation, même en devinant son id (404 dans ce cas).
            return Election.objects.get(pk=pk, organisation=organisation)
        except Election.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description="Returns a single election details",
        responses= res
    )
    def get(self, request, pk):
        if request.user.is_authenticated and  request.user.has_perm('vote.view_election'):
            election = self.get_object(pk, request.user.organisation)
            serializer = ElectionSerializer(election)
            res = {
                "data": serializer.data,
                "message": f"Election id {pk}",
                "error": False
            }
            
            return response.Response(res, status=status.HTTP_200_OK)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_description="Modify a single election details",
        request_body=openapi.Schema(
            description="Request body for election creation",
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="name", default="name election", required=[]),
                'begin_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="begin date timestamp", required=[]),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="end date timestamp", required=[]),
                # 'state': openapi.Schema(type=openapi.TYPE_STRING, description="state"),
            },
        ),
        responses= res
    )
    def put(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated and  request.user.has_perm('vote.change_election'):
            election = self.get_object(pk, request.user.organisation)
            serializer = ElectionSerializer(election, data=request.data, partial=True)
            if(serializer.is_valid()):
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            print(serializer.errors)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Delete a single election by id",
        responses= {
            204:'no content',
            401: 'Unauthenticated',
            403: 'Access denied'
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated and  request.user.has_perm('vote.delete_election'):
            election = self.get_object(pk, request.user.organisation)
            election.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)
