from django.db import models

from vote.models.user import CustomUser
from .election import Election

class Candidate(models.Model):
    candidate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='candidate')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='election_candidature')
    date_candidature = models.DateTimeField()
    description = models.CharField(blank=True)
    status = models.CharField(max_length=100, choices=[
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('rejete', 'Rejeté'),
    ], default='en_attente')
    reject_message = models.CharField(blank=True)

    class Meta:
        ordering = ['-date_candidature', 'election_id']
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "election"], name="unique_candidature_par_election"
            )
        ]