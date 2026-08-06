from django.db import models

from vote.models.user import CustomUser
from vote.models.organisation import Organisation

class Election(models.Model):
    name = models.CharField(max_length= 100)
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.CharField(max_length=1000)
    state = models.CharField(max_length=100, choices=[
        ('a_venir', 'A venir'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée')
    ], default='a_venir')
    # Organisation propriétaire de l'élection : toute la logique de cloisonnement
    # (listes, détails, vote, candidatures, résultats) filtre par ce champ.
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='elections')
    supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='supervisor')
    electors = models.ManyToManyField(CustomUser, through="Vote", through_fields=('election', 'elector')) # cles etrangeres a preciser pour le vote
    candidates = models.ManyToManyField(CustomUser, through="Candidate", related_name='candidates') 

    def __str__(self):
        return f"{self.name} - start at {self.begin_date} end at {self.end_date} current state {self.state}"

    class Meta:
        ordering = ['begin_date', 'end_date']
