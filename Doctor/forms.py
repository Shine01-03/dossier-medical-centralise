from django import forms
from django.contrib.auth.models import User
from .models import  Medecin

AVATAR_CHOICES = [
    ('avatar1.jpeg', 'Avatar 1'),
    ('avatar2.png', 'Avatar 2'),
    ('avatar3.png', 'Avatar 3'),
]

class DoctorProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Medecin
        fields = ['specialite', 'sexe', 'avatar']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = user.username
        self.fields['email'].initial = user.email

    def save(self, commit=True):
        doctor = super().save(commit=False)
        user = doctor.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            doctor.save()
        return doctor


   
class MedecinCreationForm(forms.Form):
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

        


class AuthentificationCreationForm(forms.Form):
    

    username = forms.CharField(max_length=150, widget= forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget= forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    specialite= forms.CharField(max_length= 150, widget= forms.TextInput(attrs={'class':'form-control'}))

    

    class Meta:
        
        model = Medecin
        fields = ['username', 'email', 'password', 'specialite']
