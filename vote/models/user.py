from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import random

from vote.manager import CustomUserManager

def random_matricule():
    return random.randint(1,10000)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    sex = models.CharField(max_length=1, choices=[
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    ], default='M')
    birth_date = models.DateField(default=timezone.now().date())
    #matricule = models.PositiveBigIntegerField(default=random_matricule())
    is_elector = models.BooleanField(default=True)
    is_supervisor = models.BooleanField(default=False)
    is_candidate = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email} de nom {self.first_name} {self.last_name} '