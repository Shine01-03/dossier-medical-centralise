from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Medecin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    
    specialite = models.CharField(max_length=100, blank=True, null=True)
    # ajoute d'autres champs si besoin

    def __str__(self):
        return f"{self.user.username} - Médecin"
    


class Patient(models.Model):
    matricule = models.CharField(max_length=20, unique=True, blank=True)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    adresse = models.CharField(max_length=255)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')])

    def save(self, *args, **kwargs):
        if not self.matricule:
            last_id = Patient.objects.count() + 1
            self.matricule = f"PAT{last_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.prenoms}"
    

class RendezVous(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    heure = models.TimeField()
    motif = models.TextField(blank=True)

    def __str__(self):
        return f"RDV - {self.patient} le {self.date} à {self.heure}"


