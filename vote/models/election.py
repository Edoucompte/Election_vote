from django.db import models
from .superviseur import ProfilSuperviseur
from .electeur import ProfilElecteur

class Election(models.Model):
    nom = models.CharField(max_length= 100)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    etat = models.CharField(max_length=100, choices=[
        ('a_venir', 'A venir'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée')
    ], default='a_venir')
    superviseur = models.ForeignKey(ProfilSuperviseur, on_delete=models.CASCADE, related_name='superviseur')
    electeurs = models.ManyToManyField(ProfilElecteur, through="Vote", through_fields=('election', 'electeur')) # cles etrangeres a preciser pour le vote
    candidats = models.ManyToManyField(ProfilElecteur, through="Candidature", related_name='candidats') 

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['date_debut', 'date_fin']
