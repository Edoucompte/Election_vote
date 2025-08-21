from django.db import models

from vote.models.user import CustomUser

class Election(models.Model):
    nom = models.CharField(max_length= 100)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    etat = models.CharField(max_length=100, choices=[
        ('a_venir', 'A venir'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée')
    ], default='a_venir')
    superviseur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='superviseur')
    electeurs = models.ManyToManyField(CustomUser, through="Vote", through_fields=('election', 'electeur')) # cles etrangeres a preciser pour le vote
    candidats = models.ManyToManyField(CustomUser, through="Candidature", related_name='candidats') 

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['date_debut', 'date_fin']
