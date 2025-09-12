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
    permission_classes = [ IsSupervisor ]
    authentication_classes = [CustomAuthentication]
    
    @swagger_auto_schema(
        operation_description="Returns elections list",
        responses= res
    )
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and  request.user.has_perm('vote.view_election'):
            elections = Election.objects.all()
            paginator =PageNumberPagination()
            paginator_queryset = paginator.paginate_queryset(elections, request)
            serializer = ElectionSerializer(paginator_queryset, many=True)
            # print("results", paginator.get_results(serializer.validated_data))
            return response.Response({
                "data": CustomPaginator.format_json_response(paginator, serializer.validated_data), # , serializer.validated_data
                "details": "Liste des elections",
                "succes": True
            }, status=status.HTTP_200_OK)
            
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

    
    @swagger_auto_schema(
        operation_description="Create new election",
        request_body=ElectionSerializer,
        responses= res
    )
    def post(self, request):
        serializer = ElectionSerializer(data=request.data)
        if(serializer.is_valid):
            serializer.save()
            return response.Response(serializer.validated_data, status=status.HTTP_201_CREATED)
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
            "data": serializer.validated_data,
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
            return response.Response(serializer.validated_data, status=status.HTTP_200_OK)
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
