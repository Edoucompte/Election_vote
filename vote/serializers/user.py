from rest_framework import serializers
from vote.encryption import hashPassword
from vote.models import CustomUser
from django.contrib.auth.models import Group

class UserListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        users = [CustomUser(**user) for user in validated_data]
        return CustomUser.objects.bulk_create(users)

class CustomUserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(read_only=True)
    # token = serializers.CharField(max_length=128, read_only=True)
    # token_expiration = serializers.DateTimeField( read_only=True)
    class Meta:
        model = CustomUser
        list_serializer_class = UserListSerializer
        # fields = ['id', 'first_name', 'last_name', 'email', 'sexe', 'date_joined', 'date_naissance', 'matricule', 'is_active', 'is_staff']
        exclude = ('is_staff', 'is_superuser', 'user_permissions')
        read_only_fields = ['token', 'token_expiration', 'password']
    
    def create(self, validated_data):
        # password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        if(validated_data.get('is_supervisor')):
            print('Supervisor Creation')
            setattr(user, 'is_staff', True)
            setattr(user, 'is_superuser', True)
        # setattr(user, 'password', hashPassword(password) )
        #user['password'] = hashPassword(password) #.set_password(password)
        user.save()

        if(not user.is_supervisor):
            print('USer adding to elector group')
            elector_group, created = Group.objects.get_or_create("Elector")
            user.groups.add(elector_group)
        return user
        

    def update(self, instance, validated_data):
        print("from update serialiswer", validated_data)
        # password = validated_data.pop('password')
        if(validated_data.get('is_electeur')):
            instance['is_staff'] = True
            instance['is_superuser'] = True
        # if(password):
        #     instance.password = hashPassword(password) #.set_password(password)
        for key,value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_supervisor = serializers.BooleanField(read_only=True)
    is_elector = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CustomUser
        # fields = ['id', 'first_name', 'last_name', 'email', 'sexe', 'date_joined', 'date_naissance', 'matricule', 'is_active', 'is_staff']
        exclude = ('is_staff', 'is_superuser', 'user_permissions')
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        setattr(user, 'password', hashPassword(password) )
        #user['password'] = hashPassword(password) #.set_password(password)
        user.save()

        elector_group, created = Group.objects.get_or_create("Elector")
        user.groups.add(elector_group)
        return user

class UsersFileSerializer(serializers.Serializer):
    creation = serializers.FileField()
