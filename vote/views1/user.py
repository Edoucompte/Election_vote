from vote.models import CustomUser
from rest_framework.views import APIView
from rest_framework import parsers
from vote.paginations import CustomPaginator
from rest_framework.pagination import PageNumberPagination
from rest_framework import response, status, authentication, exceptions, permissions
from vote.permissions import IsSupervisor
from vote.serializers import CustomUserSerializer
from django.http import Http404
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from vote.encryption import decodeToken
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import pandas as pd
import random
import string

from vote.serializers.user import UserListSerializer, UsersFileSerializer

res = {
    200: " Success ",
    401: "Unauthenticated",
    403: "Access denied"
}

def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

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
            print(payload)
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
    # permission_classes = [permissions.DjangoModelPermissions]
    
    #permission_classes = [IsAuthenticated] # [IsSupervisor]
    
    @swagger_auto_schema(
        operation_description="Returns users list",
        responses=res
    )
    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated and  request.user.has_perm('vote.view_cutomuser'):
            users = CustomUser.objects.all()
            # paginator =PageNumberPagination()
            # paginator_queryset = paginator.paginate_queryset(users, request)
            serializer = CustomUserSerializer(users, many=True)
            # print("results", paginator.get_results(serializer.data))
            return response.Response({
                "data": serializer.data, #CustomPaginator.format_json_response(paginator, serializer.data), # , 
                "details": "Liste des utilisateurs",
                "succes": True
            }, status=status.HTTP_200_OK)
        return response.Response({
            "details": "Access denied",
            "succes": False
        }, status=status.HTTP_403_FORBIDDEN)


    @swagger_auto_schema(
        operation_description="Returns users list",
        request_body=openapi.Schema(
            description="Request body for user(s) creation",
            type=openapi.TYPE_OBJECT,
            properties={
                "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="user fisrt name"),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING, description="user name name"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="user email"),
                "sex": openapi.Schema(type=openapi.TYPE_STRING, description="user sex M or F", enum=['M', 'F']),
                "birth_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="user birthday date"),
                "is_elector": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="bool for user's role", default=True),
                "is_supervisor": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="bool for user's role", default=False),
                "is_candidate": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="bool for user's role", default=True),
                # 'state': openapi.Schema(type=openapi.TYPE_STRING, description="state"),
            },
        ),
        responses=res
    )
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data, many=False)
        res = {
            "details": "Creation d'utilisateur",
        }
        if(serializer.is_valid()):
            serializer.save()
            res['success'] = True
            res['data'] = serializer.data
            reset_password_token = generate_random_string(100)
            try :
                send_mail(
                    'Super Vote Definition de mot de passe', 
                    f""" 
                        M/Mme {serializer.data['first_name']} {serializer.data['last_name']},
                        Un administrateur de la plateforme Super Vote
                        vient de vous créer un compte Electeur. Veuillez cliquer sur le lien suivant pour choisir un mot de passe:
                        http://localhost:5173/setPassword/{reset_password_token}
                    """, 
                    'super@vote.com', 
                    [serializer.data['email']], 
                    fail_silently=False
                )
            except :
                print('Mail sending failed. Check the SMTP server.')
            return response.Response(res, status=status.HTTP_201_CREATED)
        res['success'] = False
        res['data'] = serializer.errors
        return response.Response(res, status=status.HTTP_400_BAD_REQUEST)

class CustomUserDetailView(APIView):
    '''
        Users View
    '''

    authentication_classes = [CustomAuthentication]
    # permission_classes = [permissions.DjangoModelPermissions]
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
        return response.Response({"succes": False, "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Returns users list",
        responses={
            204:'no content',
            401: 'Unauthenticated',
            403: 'Access denied'
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        user.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

class MassUserView(APIView):
    authentication_classes = [CustomAuthentication]
    parser_classes = [parsers.MultiPartParser]
    
    @swagger_auto_schema(
        operation_description="Returns users list",
        manual_parameters=[
            openapi.Parameter(
                name='creation',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='Excel or csv file for create',
                required=True
            )
        ],
        responses=res
    )
    def post(self, request):
        # print(request.data) # contains form data if parsers.MultiPartParser and parsers.FormParser
        # print(request.FILES) # MultiValueDict dict of uploaded files
        file_serializer = UsersFileSerializer(data=request.data)
        # print('request ', request.FILES['creation'])
        res = {
            "details": "Creation d'utilisateurs",
        }
        if(file_serializer.is_valid()):
            # res['data'] = list_serializer.data
            # print('serialized data', file_serializer.data)
            try:
                df = pd.read_excel(file_serializer.validated_data['creation'])
                df['birth_date'] = pd.to_datetime(df['birth_date']).dt.date #date string converts to date type
                # print('dict', df)
                data = df.to_dict(orient='records')
                # print('data ', data)
                serializer = CustomUserSerializer(data=data, many=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                ids = [user['id'] for user in serializer.data ]
                newUserAdded = CustomUser.objects.filter(id__in=ids)
                elector_group, created = Group.objects.get_or_create("Elector")
                elector_group.user_set.add(*newUserAdded)
                
                # print('newUsers', newUserAdded, 'serializer', serializer.data)
                identifiants = [(user['email'], f"{user['last_name']} {user['first_name']}") for user in serializer.data ]
                for identifiant in identifiants:
                    reset_password_token = generate_random_string(100)
                    try:
                        send_mail(
                            'Super Vote Definition de mot de passe', 
                            f"""
                                M/Mme  ${identifiant[1]},
                                Un administrateur de la plateforme Super Vote
                                vient de vous créer un compte Electeur. Veuillez cliquer sur le lien suivant pour choisir un mot de passe:
                                http://localhost:5173/setPassword/{reset_password_token}
                            """, 
                            'super@vote.com', 
                            [identifiant[0]], 
                            fail_silently=False
                        )
                    except :
                        print(f" Erreur lors de l'envoi de mail a {identifiant[0]} ")
                
                res['data'] = serializer.data
                res['success'] = True
                return response.Response(res, status=status.HTTP_201_CREATED)
            except Exception as e:
                res['success'] = False
                res['errors'] = str(e)
                return response.Response(res, status=status.HTTP_400_BAD_REQUEST)
        # print('validation error')
        res['success'] = False
        res['errors'] = file_serializer.errors
        return response.Response(res, status=status.HTTP_400_BAD_REQUEST)
        
        # if(serializer.is_valid()):
        #     serializer.save()
        #     res['success'] = True
        #     res['data'] = serializer.data
        #     return response.Response(res, status=status.HTTP_201_CREATED)
        # res['success'] = False
        # res['data'] = serializer.errors
        # return response.Response(res, status=status.HTTP_400_BAD_REQUEST)