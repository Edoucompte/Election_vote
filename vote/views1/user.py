from vote.models import CustomUser
from rest_framework.views import APIView
from vote.paginations import CustomPaginator
from rest_framework.pagination import PageNumberPagination
from rest_framework import response, status, authentication, exceptions, permissions
from vote.permissions import IsSupervisor
from vote.serializers import CustomUserSerializer
from django.http import Http404
from vote.encryption import decodeToken
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

res = {
    200: " Success ",
    401: "Unauthenticated",
    403: "Access denied"
}

class CustomAuthentication(authentication.BasicAuthentication):
    def authenticate(self, request):
        #extraire le token du header
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None
        
        #decrypter token jwt
        secret = str(os.getenv('SECRET_KEY'))
        try:
            payload = decodeToken(token, secret)
            # print(payload)
        except Exception as e:
            raise exceptions.AuthenticationFailed("Invalid token")

        # verifier le user
        try:
            user = CustomUser.objects.get(id=int(payload.get('sub')), email=payload.get('email') )
            print(user)
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, token)

class CustomUserView(APIView):

    authentication_classes = [CustomAuthentication]
    permission_classes = [permissions.DjangoModelPermissions]
    
    #permission_classes = [IsAuthenticated] # [IsSupervisor]
    
    @swagger_auto_schema(
        operation_description="Returns users list",
        responses=res
    )
    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated and  request.user.has_perm('vote.view_cutomuser'):
            users = CustomUser.objects.all()
            paginator =PageNumberPagination()
            paginator_queryset = paginator.paginate_queryset(users, request)
            serializer = CustomUserSerializer(paginator_queryset, many=True)
            # print("results", paginator.get_results(serializer.data))
            return response.Response({
                "data": CustomPaginator.format_json_response(paginator, serializer.data), # , serializer.validated_data
                "details": "Liste des utilisateurs",
                "succes": True
            }, status=status.HTTP_200_OK)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Returns users list",
        request_body=CustomUserSerializer,
        responses=res
    )
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data, many=True)
        res = {
            "details": "Creation d'utilisateurs",
        }
        if(serializer.is_valid()):
            serializer.save()
            res['success'] = True
            res['data'] = serializer.data
            return response.Response(res, status=status.HTTP_201_CREATED)
        res['success'] = False
        res['data'] = serializer.errors
        return response.Response(res, status=status.HTTP_400_BAD_REQUEST)

class CustomUserDetailView(APIView):
    '''
        Users View
    '''

    authentication_classes = [CustomAuthentication]
    permission_classes = [permissions.DjangoModelPermissions]
    # permission_classes = [IsAdminUser] # [IsSupervisor]
    # permission_classes =[IsAuthenticatedOrReadOnly]


    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Returns users list",
        responses=res
    ) 
    def get(self, request, pk):
        if(request.user.is_authenticated and request.user.has_perm('vote.view_customuser')):
            user = self.get_object(pk)
            serializer = CustomUserSerializer(user)
            res = {
                "data": serializer.data,
                "message": f"Utilisateur id {pk}",
                "error": False
            }
            
            return response.Response(res, status=status.HTTP_200_OK)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_description="Returns users list",
        request_body=CustomUserSerializer,
        responses= res
    )
    def put(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Returns users list",
        responses={
            204:'no contente',
            401: 'Unauthenticated',
            403: 'Access denied'
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        user.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
