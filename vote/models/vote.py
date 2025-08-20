from django.db import models
from .electeur  import ProfilElecteur
from .election import Election

class Vote(models.Model):
    electeur = models.ForeignKey(ProfilElecteur, on_delete=models.CASCADE, related_name='electeur')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='election_vote')
    date_vote = models.DateField()
    candidat = models.OneToOneField(ProfilElecteur, on_delete=models.CASCADE, 
        related_name="vote_candidat", null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["electeur", "election"], name="unique_vote_par_election"
            )
        ]