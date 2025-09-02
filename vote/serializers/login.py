from rest_framework import serializers
import re

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def password_validate(self, value):
        # au moins un min, un majuscule, un chiffre, un carac. spec, et au moins 8 carac avec des look ahead
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$&!%?*])[A-Za-z\d@$&!%?*]{8,}$', value): 
            raise serializers.ValidationError('Password form incorrect')
        return value