from rest_framework.views import APIView
from rest_framework import response, status
from vote.models import Vote
from vote.serializers import VoteSerializer
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from vote.views1.user import res

class VoteView(APIView):
    # @swagger_auto_schema(
    #     operation_description="Returns votes list",
    #     responses= res
    # )
    # def get(self, request, *args, **kwargs):
    #     votes = Vote.objects.all()
    #     serializer = VoteSerializer(votes, many=True)
    #     responserJson = {
    #         "data": serializer.validated_data,
    #         "message": "Liste des votes",
    #         "error": False
    #     }
        
    #     return response.Response(responserJson, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Make a vote",
        request_body=VoteSerializer,
        responses= res
    )
    def post(self, request, election_id):
        serializer = VoteSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return response.Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VoteDetailView(APIView):
    def get_object(self, pk):
        try:
            return Vote.objects.get(pk=pk)
        except Vote.DoesNotExist:
            raise Http404
    
    # @swagger_auto_schema(
    #     operation_description="Returns a single vote details",
    #     responses= res
    # )     
    # def get(self, request, pk):
    #     Vote = self.get_object(pk)
    #     serializer = VoteSerializer(Vote)
    #     res = {
    #         "data": serializer.validated_data,
    #         "message": f"Vote id {pk}",
    #         "error": False
    #     }
        
    #     return response.Response(res, status=status.HTTP_200_OK)

    # @swagger_auto_schema(
    #     operation_description="Modify a single vote details",
    #     request_body=VoteSerializer,
    #     responses= res
    # )
    # def put(self, request, pk, *args, **kwargs):
    #     Vote = self.get_object(pk)
    #     serializer = VoteSerializer(Vote, data=request.data, partial=True)
    #     if(serializer.is_valid()):
    #         serializer.save()
    #         return response.Response(serializer.validated_data, status=status.HTTP_200_OK)
    #     print(serializer.errors)
    #     return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def delete(self, request, pk, *args, **kwargs):
    #     Vote = self.get_object(pk)
    #     Vote.delete()
    #     return response.Response(status=status.HTTP_204_NO_CONTENT)
