from django.db import models
from .user import CustomUser

class ProfilElecteur(models.Model):
    user = models.OneToOneField(
        to=CustomUser,
        on_delete= models.CASCADE,
        primary_key=True,
        related_name='electeur',
    )

    def __str__(self):
        return self.user