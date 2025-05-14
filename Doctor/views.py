from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import Patient, Medecin, RendezVous
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseForbidden




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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie.")
            return redirect('index')  
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            return render(request, 'doctor/login.html')
    
    return render(request, 'doctor/login.html')

def deconnexion(request):
    logout(request)  # Supprime les données de session et déconnecte l'utilisateur
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
