from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import Patient, Medecin, RendezVous
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DoctorProfileForm, MedecinCreationForm
from django.contrib.admin.views.decorators import staff_member_required
import random
import string
from django.contrib.auth.models import User


# Create your views here.

def index(request):
    return render(request, 'admin/index.html')


def statistiques_donnees(request):
    # On groupe par mois avec TruncMonth
    data = (
        RendezVous.objects
        .annotate(mois=TruncMonth('date'))
        .values('mois')
        .annotate(total=Count('id'))
        .order_by('mois')
    )

    categories = []
    valeurs = []

    for item in data:
        categories.append(item['mois'].strftime('%Y-%m-%d'))  # format ISO
        valeurs.append(item['total'])

    return JsonResponse({
        'categories': categories,
        'series': [{
            'name': 'Rendez-vous',
            'data': valeurs
        }]
    })


def details_rendezvous(request):
    rdvs = RendezVous.objects.select_related('patient').order_by('-date')
    return render(request, 'doctor/details_rendezvous.html', {'rdvs': rdvs})


def ajouter_patient(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenoms = request.POST.get('prenoms')
        adresse = request.POST.get('adresse')
        date_naissance = request.POST.get('date_naissance')
        sexe = request.POST.get('sexe')

        # Créer un nouvel objet Patient
        patient = Patient(
            nom=nom,
            prenoms=prenoms,
            adresse=adresse,
            date_naissance=date_naissance,
            sexe=sexe
        )
        patient.save()

        return JsonResponse({'status': 'success', 'message': 'Patient ajouté avec succès.'})

    return render(request, 'doctor/ajouter_patient.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'doctor/login.html')

 
def deconnexion(request):
    logout(request)  
    return redirect('index')


def tableau_de_bord(request):
    is_medecin = Medecin.objects.filter(user=request.user).exists()
    return render(request, 'dashboard.html', {'is_medecin': is_medecin})

def medecin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if Medecin.objects.filter(user=request.user).exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Accès réservé aux médecins.")
    return wrapper


@login_required
def mon_profil(request):
    doctor = Medecin.objects.get(user=request.user)
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('mon_profil')
    else:
        form = DoctorProfileForm(instance=doctor, user=request.user)
    return render(request, 'doctor/mon_profil.html', {'form': form})


@staff_member_required
def ajouter_medecin(request):
    if request.method == 'POST':
        form = MedecinCreationForm(request.POST, request.FILES)
        if form.is_valid():
            

            # Champs récupérés depuis le formulaire
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['nom'],
            last_name=form.cleaned_data['prenoms'],
            email=form.cleaned_data['email'],

            )
            user_id = user.id
            specialite=form.cleaned_data['specialite']
            sexe=form.cleaned_data['sexe']


            medecin = Medecin(user= user, specialite= specialite, sexe=sexe)
            medecin.save()
            messages.success(request, "Médecin ajouté avec succès!")

        
            return redirect('liste_medecins')
    else:
        form = MedecinCreationForm()
    
    return render(request, 'admin/ajouter_medecin.html', {'form': form})


@staff_member_required
def liste_medecins(request):
    sort = request.GET.get('sort')

    if sort == 'nom':
        medecins = Medecin.objects.all().order_by('last_name')
    elif sort == 'prenom':
        medecins = Medecin.objects.all().order_by('first_name')
    elif sort == 'date':
        medecins = Medecin.objects.all().order_by('-created_at')
    else:
        medecins = Medecin.objects.all()

    return render(request, 'admin/liste_medecins.html', {'medecins': medecins})

def gestion_medecins(request):
    medecins = Medecin.objects.all()
    return render(request, 'admin/gestion_medecins.html', {'medecins': medecins})

def modifier_medecin(request, medecin_id):
    medecin = Medecin.objects.get(id=medecin_id)
    if request.method == 'POST':
        form = MedecinCreationForm(request.POST, request.FILES, instance=medecin)
        if form.is_valid():
            form.save()
            return redirect('liste_medecins')
    else:
        form = MedecinCreationForm(instance=medecin)
    return render(request, 'admin/modifier_medecin.html', {'form': form, 'medecin': medecin})


def supprimer_medecin(request, medecin_id):
    medecin = Medecin.objects.get(id=medecin_id)
    if request.method == 'POST':
        medecin.delete()
        return redirect('liste_medecins')
    return render(request, 'admin/supprimer_medecin.html', {'medecin': medecin})