from django.db import models

from vote.models.user import CustomUser
from .election import Election

class Vote(models.Model):
    elector = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='elector')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='election_vote')
    date_vote = models.DateTimeField()
    candidate = models.OneToOneField(CustomUser, on_delete=models.CASCADE, 
        related_name="vote_candidate", null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["elector", "election"], name="unique_vote_par_election"
            )
        ]