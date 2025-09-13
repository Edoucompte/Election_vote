from django.db import models

from vote.models.user import CustomUser
from .election import Election

class Candidate(models.Model):
    candidate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='candidate')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='election_candidature')
    date_candidature = models.DateTimeField()
    description = models.CharField(blank=True)
    is_accepted = models.CharField(default=False)
    reject_message = models.CharField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "election"], name="unique_candidature_par_election"
            )
        ]