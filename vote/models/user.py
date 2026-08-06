from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import random

from vote.manager import CustomUserManager
from vote.models.organisation import Organisation

def random_matricule():
    return random.randint(1,10000)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    password = models.CharField(_("password"), max_length=128, null=True)
    token = models.CharField(max_length=128, null=True)
    token_expiration = models.DateTimeField( null=True)
    # Organisation (compte) à laquelle appartient cet utilisateur. Null uniquement
    # pour un éventuel super-admin plateforme (créé via createsuperuser) qui n'a
    # pas vocation à appartenir à une organisation cliente.
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )
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