from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import date

# Create your models here.
class Medecin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    
    specialite = models.CharField(max_length=100, blank=True, null=True)
    sexe = models.CharField(max_length=10, choices=[('Homme', 'Homme'), ('Femme', 'Femme')], null= True, blank = True)

    photo_profil = models.ImageField(null= True, blank= True)
    # ajoute d'autres champs si besoin

    def __str__(self):
        return f"{self.user.username} - Médecin"
    



class Patient(models.Model):
    # Identité
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient', null=True, blank=True)
    matricule = models.CharField(max_length=20, unique=True, blank=True, null=True)  
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=10, choices=[("M", "Masculin"), ("F", "Féminin")])

    # Contact & Authentification
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    # Infos médicales complémentaires
    groupe_sanguin = models.CharField(
        max_length=3, blank=True, null=True,
        choices=[("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
                 ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-")]
    )
    adresse = models.TextField(blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    situation_matrimoniale = models.CharField(max_length=50, blank=True, null=True)

    # Personne à prévenir
    personne_a_prevenir = models.CharField(max_length=100, blank=True, null=True)
    tel_personne_prevenir = models.CharField(max_length=20, blank=True, null=True)

    # Dates de suivi
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Génération automatique du matricule si absent
        if not self.matricule:
            self.matricule = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        
        # Si le mot de passe n’est pas encore haché → on le hache avant sauvegarde
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    @property
    def age(self):
        today = date.today()
        # Calcul de l'âge
        age = today.year - self.date_naissance.year
        # On ajuste si la date d'anniversaire n'est pas encore passée cette année
        if (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day):
            age -= 1
        return age


    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.matricule})"
   

class RendezVous(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
        ('termine', 'Terminé'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medecin = models.ForeignKey(User, on_delete=models.CASCADE)  # le médecin qui reçoit
    date = models.DateField()
    heure = models.TimeField()
    motif = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')

    def __str__(self):
        return f"RDV - {self.patient} le {self.date} à {self.heure}"



        
        

class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)
    diagnostic = models.TextField()
    traitement = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    terminee = models.BooleanField(default=True)  # Indique si la consultation est clôturée

    def __str__(self):
        return f"Consultation de {self.patient} le {self.date}"
    

class Fonctionnalite(models.Model):
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    STATUT_CHOICES = [
        ('Disponible', 'Disponible'),
        ('En développement', 'En développement'),
        ('En test', 'En test'),
        ('Désactivée', 'Désactivée'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='Disponible')

    def __str__(self):
        return self.nom    


class Antecedent(models.Model):
    TYPE_CHOICES = [
        ('allergie', 'Allergie'),
        ('maladie_chronique', 'Maladie chronique'),
        ('medical', 'Antécédent médical'),
        ('chirurgical', 'Antécédent chirurgical'),
        ('diagnostic', 'Diagnostic en cours'),
        ('critique', 'Information critique'),
        ('autre', 'Autre'),

    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='antecedents')
    medecin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_staff': True})
    type_antecedent = models.CharField(max_length=50, choices=TYPE_CHOICES)
    description = models.TextField()
    date = models.DateField(default=timezone.now)
    important = models.BooleanField(default=False, help_text="Est-ce un antécédent vital pour le traitement ?")

    def __str__(self):
        return f"{self.type_antecedent} - {self.patient} - {self.date.strftime('%d/%m/%Y')}"
    


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    medecin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_staff': True})
    date_prescription = models.DateTimeField(default=timezone.now)
    remarques = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Prescription {self.id} - {self.patient.nom} {self.patient.prenoms} - {self.date_prescription.strftime('%d/%m/%Y')}"


class MedicamentPrescrit(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicaments')
    nom_medicament = models.CharField(max_length=255)
    posologie = models.TextField()
    duree_traitement = models.PositiveIntegerField(help_text="Durée en jours")

    def __str__(self):
        return f"{self.nom_medicament} ({self.duree_traitement} jours)"
