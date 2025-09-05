from django.http import Http404
from rest_framework.decorators import api_view, authentication_classes
from rest_framework import response, status
from vote.encryption import createToken, checkPassword

from vote.models import CustomUser
from vote.serializers import LoginSerializer
from vote.views1 import CustomAuthentication
import os

@api_view(['POST'])
#@authentication_classes()
def login(request):
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


@api_view(['POST'])
@authentication_classes([CustomAuthentication])
def refresh(request):
    authUser = request.user
    if( authUser): # not isinstance(authUser, AnonymousUser)
        return response.Response({
            "refresh": createToken(authUser.id, authUser.email, str(os.getenv('SECRET_KEY')) , 1*24*60*60)
        }, status=status.HTTP_200_OK)
    return  response.Response({
        "details": "Email or password incorrect"
    }, status=status.HTTP_400_BAD_REQUEST)
