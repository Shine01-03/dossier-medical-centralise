from django import forms
from django.contrib.auth.models import User
from .models import  Medecin, Patient, Antecedent, Prescription, MedicamentPrescrit

AVATAR_CHOICES = [
    ('avatar1.jpeg', 'Avatar 1'),
    ('avatar2.png', 'Avatar 2'),
    ('avatar3.png', 'Avatar 3'),
]


class DoctorProfileForm(forms.ModelForm):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Nom")
    last_name = forms.CharField(label="Prénom(s)")
    photo_profil = forms.ImageField(label="Photo de profil", required=False)
    class Meta:
        model = Medecin
        fields = ['specialite', 'sexe', 'photo_profil']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        medecin = super().save(commit=False)
        user = medecin.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            medecin.save()
        return medecin


   
class MedecinCreationForm(forms.ModelForm):
    choix = [
        ('', 'Selectionnez'),
        ('Homme', 'Homme'),
        ('Femme', 'Femme')
    ]
    username = forms.CharField(max_length=150, widget= forms.TextInput(attrs={'class':'form-control'}))
    nom = forms.CharField(max_length=100, widget= forms.TextInput(attrs={'class':'form-control'}))
    prenoms = forms.CharField(max_length=100, widget= forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget= forms.EmailInput(attrs={'class':'form-control'}))
    sexe = forms.ChoiceField(choices= choix, widget= forms.Select(attrs={'class':'form-control'}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    specialite= forms.CharField(max_length= 150, widget= forms.TextInput(attrs={'class':'form-control'}))

    

    class Meta:
        model = Medecin
        fields = ['username', 'nom', 'prenoms', 'email', 'sexe', 'password', 'specialite']

        

class MedecinModificationForm(forms.ModelForm):
    class Meta:
        model = Medecin
        fields = ['specialite', 'sexe', 'photo_profil']



class AuthentificationCreationForm(forms.Form):
    

    username = forms.CharField(max_length=150, widget= forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget= forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    specialite= forms.CharField(max_length= 150, widget= forms.TextInput(attrs={'class':'form-control'}))

    

    class Meta:
        
        model = Medecin
        fields = ['username', 'email', 'password', 'specialite']


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }       


class AntecedentForm(forms.ModelForm):
    class Meta:
        model = Antecedent
        fields = ['type_antecedent', 'description', 'important']
        widgets = {
            'type_antecedent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['remarques']
        widgets = {
            'remarques': forms.Textarea(attrs={
                'class': 'form-control',  
                'rows': 4,
                'placeholder': 'Remarques facultatives…'
            }),
        }


class MedicamentPrescritForm(forms.ModelForm):
    class Meta:
        model = MedicamentPrescrit
        fields = ['nom_medicament', 'posologie', 'duree_traitement']
        widgets = {
            'nom_medicament': forms.TextInput(attrs={'class': 'form-control'}),
            'posologie': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duree_traitement': forms.NumberInput(attrs={'class': 'form-control'}),
        }

