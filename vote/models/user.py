from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from vote.managerr import CustomUserManager

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    sexe = models.CharField(max_length=1, choices=[
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    ])
    date_naissance = models.DateField()
    matricule = models.BigIntegerField()
    is_electeur = models.BooleanField(default=False)
    is_superviseur = models.BooleanField(default=False)
    is_candidat = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager

    def __str__(self):
        return f'{self.email} avec {self.matricule}'