from rest_framework.views import APIView
from rest_framework import response, status
from vote.models import Vote, Election
from vote.serializers import VoteSerializer
from django.http import Http404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from vote.views1.user import CustomAuthentication, res

class VoteView(APIView):
    authentication_classes = [CustomAuthentication]
    # @swagger_auto_schema(
    #     operation_description="Returns votes list",
    #     responses= res
    # )
    # def get(self, request, *args, **kwargs):
    #     votes = Vote.objects.all()
    #     serializer = VoteSerializer(votes, many=True)
    #     responserJson = {
    #         "data": serializer.data,
    #         "message": "Liste des votes",
    #         "error": False
    #     }
        
    #     return response.Response(responserJson, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Make a vote",
        request_body=openapi.Schema(
            description="Request body for election creation",
            title="Election creation params",
            type=openapi.TYPE_OBJECT,
            properties={
                'date_vote': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="begin date timestamp"),
                'election': openapi.Schema(type=openapi.TYPE_INTEGER, description="Id of election"),
                'candidate': openapi.Schema(type=openapi.TYPE_INTEGER, description="Id of candidate")
            },
        ),
        # manual_parameters=openapi.Parameter(name="elector_")
        responses= res
    )
    def post(self, request):
        # NB : le paramètre `election_id` a été retiré, l'URL `votes/` ne le
        # fournit pas (elle ne le fournissait jamais : cet endpoint plantait
        # systématiquement en TypeError avant ce correctif). L'id de l'élection
        # est lu depuis le corps de la requête, comme documenté par le schéma
        # swagger ci-dessus.
        if request.user.is_authenticated and  request.user.has_perm('vote.add_vote'):
            # Empêche de voter pour une élection d'une autre organisation,
            # même en connaissant/devinant son id.
            election = Election.objects.filter(
                pk=request.data.get('election'), organisation=request.user.organisation
            ).first()
            if election is None:
                return response.Response({
                    "succes": False,
                    "errors": "Élection introuvable."
                }, status=status.HTTP_404_NOT_FOUND)
            # Un vote hors de la fenêtre begin_date/end_date n'était jusqu'ici
            # jamais rejeté par l'API (seul le front empêchait l'accès, ce qui
            # ne protège rien contre un appel direct à l'API).
            now = timezone.now()
            if not (election.begin_date <= now <= election.end_date):
                return response.Response({
                    "succes": False,
                    "errors": "Le vote n'est pas ouvert pour cette élection."
                }, status=status.HTTP_400_BAD_REQUEST)
            # NB : le double vote est déjà rejeté proprement par la contrainte
            # unique (elector, election) du modèle, exposée automatiquement par
            # VoteSerializer comme erreur de validation (vérifié).
            data = request.data
            data["elector"] = request.user.id # injection of elector from connected user
            serializer = VoteSerializer(data=data)
            if(serializer.is_valid()):
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return response.Response({"succes": False, "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

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
    #         "data": serializer.data,
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
    #         return response.Response(serializer.data, status=status.HTTP_200_OK)
    #     print(serializer.errors)
    #     return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def delete(self, request, pk, *args, **kwargs):
    #     Vote = self.get_object(pk)
    #     Vote.delete()
    #     return response.Response(status=status.HTTP_204_NO_CONTENT)
