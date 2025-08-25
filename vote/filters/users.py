import django_filters
from vote.models import CustomUser

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = CustomUser
        fields = {
            'first_name': ['icontains'],
            'matricule': ['exact']
        }