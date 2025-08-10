from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    sexe = models.CharField(max_length=1, choices=[
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    ])
    date_naissance = models.DateField()
    matricule = models.BigIntegerField()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class ProfilElecteur(models.Model):
    user = models.OneToOneField(
        to=CustomUser,
        on_delete= models.CASCADE,
        primary_key=True,
        related_name='electeur',
    )

    def __str__(self):
        return self.user

class ProfilSuperviseur(models.Model):
    user = models.OneToOneField(
        to=CustomUser,
        on_delete= models.CASCADE,
        primary_key=True,
        related_name='superviseur'
    )

    def __str__(self):
        return self.user


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