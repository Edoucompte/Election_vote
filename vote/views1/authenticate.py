from rest_framework.decorators import api_view, authentication_classes
from rest_framework import response, status
from encryption import createToken

from vote.views1.user import CustomAuthentication

@api_view(['POST'])
#@authentication_classes()
def login(request):
    #sserializer pour email et password

    # rechercher user par email

    # checker son password

    # generer les deux tokens par creationToken
    
    return response.Response({
        "access": '',
        "refresh": ''
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes(CustomAuthentication)
def refresh(request):
    return response.Response({
        "refresh": request.auth
    }, status=status.HTTP_200_OK)