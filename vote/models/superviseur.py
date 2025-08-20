from django.db import models
from .user import CustomUser

class ProfilSuperviseur(models.Model):
    user = models.OneToOneField(
        to=CustomUser,
        on_delete= models.CASCADE,
        primary_key=True,
        related_name='superviseur'
    )

    def __str__(self):
        return self.user