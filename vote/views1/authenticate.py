from django.http import Http404
from rest_framework.decorators import api_view, authentication_classes, action
from rest_framework import response, status, viewsets
from vote.encryption import createToken, checkPassword

from vote.models import CustomUser
from vote.serializers import LoginSerializer
import os

from vote.serializers import CustomUserSerializer, UserProfileSerializer
from vote.views1.user import CustomAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ConnexionView(viewsets.ViewSet):
    @swagger_auto_schema(
        method="POST",
        request_body=UserProfileSerializer,
        responses={
            200:"details: Creation de compte Electeur", 
            400: "details: Invalid credentials"
        }
    )
    @action(detail=False, methods=['POST'])
    def register(self, request):
        serializer = UserProfileSerializer(data=request.data)
        res = {
            "details": "Creation de compte Electeur",
        }
        if(serializer.is_valid()):
            serializer.save()
            res['success'] = True
            res['data'] = serializer.data
            return response.Response(res, status=status.HTTP_201_CREATED)
        res['success'] = False
        res['data'] = serializer.errors
        return response.Response(res, status=status.HTTP_400_BAD_REQUEST)

    # @authentication_classes()
    @swagger_auto_schema(
        method="POST",
        request_body=LoginSerializer,
        responses={
            200:"Succes", 
            400: "details: Invalid credentials"
        }
    )
    @action(detail=False, methods=['POST'])
    def login(self, request):
        #serializer pour email et password
        serializer = LoginSerializer(data=request.data)
        if(serializer.is_valid(raise_exception=True)):
            # rechercher user par email
            try:
                user = CustomUser.objects.get(email=serializer.data["email"])
            except CustomUser.DoesNotExist:
                raise Http404

            # checker son password
            if(not checkPassword(serializer.data["password"], user.password)):
                return response.Response({
                    "details": "Email or password incorrect"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return response.Response({
                "access": createToken(user.id, user.email, str(os.getenv('SECRET_KEY')), 6*60),
                "refresh": createToken(user.id, user.email, str(os.getenv('SECRET_KEY')), 1*24*60*60)
            }, status=status.HTTP_200_OK)
        return response.Response({
                "details": "Email or password incorrect"
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
    operation_description="Resfreh an token for auth",
    request_body=openapi.Schema(
        title="resfresh",
        type=openapi.TYPE_STRING,
        # property='refresh': openapi.Schema(type=openapi.TYPE_STRING, descripton: "Refresh token")
    )
    )
    @action(detail=False, methods=['POST'],)
    #@authentication_classes([CustomAuthentication])
    def refresh(self, request):
        authUser = request.user
        if( authUser): # not isinstance(authUser, AnonymousUser)
            return response.Response({
                "refresh": createToken(authUser.id, authUser.email, str(os.getenv('SECRET_KEY')) , 1*24*60*60)
            }, status=status.HTTP_200_OK)
        return  response.Response({
            "details": "Email or password incorrect"
        }, status=status.HTTP_400_BAD_REQUEST)

    