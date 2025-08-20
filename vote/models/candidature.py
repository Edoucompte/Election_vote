from django.db import models
from .electeur import ProfilElecteur
from .election import Election

class Candidature(models.Model):
    candidat = models.ForeignKey(ProfilElecteur, on_delete=models.CASCADE, related_name='candidat')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='election_candidature')
    date_candidature = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["candidat", "election"], name="unique_candidature_par_election"
            )
        ]