from vote.models import CustomUser
from rest_framework.views import APIView
from rest_framework import response, status, authentication, exceptions
from vote.serializers import CustomUserSerializer, UserModifySerializer
from django.http import Http404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from vote.encryption import decodeToken

class CustomAuthentication(authentication.BasicAuthentication):
    def authenticate(self, request):
        #extraire le token di header
        token = request.META.get('BEARER')
        if not token:
            return None
        
        #decrypter token jwt
        payload = decodeToken(token, "mon_secret")
        ## verifier expiration

        # verifier le user
        try:
            user = CustomUser.objects.get(id=payload.get('sub'), email=payload.get('email') )
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, token)

class CustomUserView(APIView):
    authentication_classes = [CustomAuthentication]
    #permission_classes =[IsAuthenticatedOrReadOnly]
    def get(self, request, *args, **kwargs):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        res = {
            "data": serializer.data,
            "message": "Liste des utilisateurs",
            "error": False
        }
        
        return response.Response(res, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = UserModifySerializer(data=request.data)
        if(serializer.is_valid):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomUserDetailView(APIView):
    permission_classes =[IsAuthenticatedOrReadOnly]
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user)
        res = {
            "data": serializer.data,
            "message": f"Utilisateur id {pk}",
            "error": False
        }
        
        return response.Response(res, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        serializer = UserModifySerializer(user, data=request.data)
        if(serializer.is_valid):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        user.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
