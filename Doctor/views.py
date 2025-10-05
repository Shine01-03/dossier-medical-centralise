from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from .models import Patient, Medecin, RendezVous, Consultation, Fonctionnalite, MedicamentPrescrit, Prescription
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DoctorProfileForm, MedecinCreationForm, PatientForm, AntecedentForm, PrescriptionForm, MedicamentPrescritForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.utils import timezone
from datetime import date
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import uuid
import base64
import os
from django.template.loader import render_to_string
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory
from .models import MedicamentPrescrit, Prescription, Antecedent
from django.forms import formset_factory

MedicamentFormSet = modelformset_factory(
    MedicamentPrescrit,
    form=MedicamentPrescritForm,
    extra=1,
    can_delete=True
)

def home(request):
    return render(request, 'doctor/home.html')


def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'doctor/login.html')

 
def deconnexion(request):
    logout(request)  
    messages.success(request, 'Vous avez été déconnecté avec succès.')

    return redirect('login')


def get_image_base64(path):
    with open(path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@login_required
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


@login_required
def details_rendezvous(request):
    if request.method == "POST":
        rdv_id = request.POST.get("rdv_id")
        statut = request.POST.get("status")
        try:
            rdv = RendezVous.objects.get(id=rdv_id)
            rdv.statut = statut
            rdv.save()
            messages.success(request, "✅ Statut du rendez-vous mis à jour.")
        except RendezVous.DoesNotExist:
            messages.error(request, "❌ Rendez-vous introuvable.")
        return redirect("details_rendezvous")  

    rdvs = RendezVous.objects.select_related("patient").order_by("-date")
    return render(request, "doctor/details_rendezvous.html", {"rdvs": rdvs})


@login_required
def changer_statut_rdv(request, rdv_id, statut):
    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.statut = statut
    rdv.save()
    return redirect('liste_rendezvous')

def generer_matricule():
    return "PAT" + uuid.uuid4().hex[:6].upper()


@login_required
def ajouter_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            prenoms = form.cleaned_data['prenoms']
            date_naissance = form.cleaned_data['date_naissance']

            # Vérifier s’il existe déjà un patient avec ces informations
            existe = Patient.objects.filter(nom__iexact=nom, prenoms__iexact=prenoms, date_naissance=date_naissance).exists()
            if existe:
                messages.warning(request, "Ce patient existe déjà dans la base.")
                return redirect('ajouter_patient')

            patient = form.save(commit=False)
            patient.matricule = generer_matricule()
            patient.save()
            messages.success(request, "Patient ajouté avec succès.")
            return redirect('liste_patients')
    else:
        form = PatientForm()
    return render(request, 'doctor/ajouter_patient.html', {'form': form})


def liste_patients(request):
    sort = request.GET.get('sort')

    if sort == 'nom':
        patients = Patient.objects.all().order_by('nom')
    elif sort == 'prenom':
        patients = Patient.objects.all().order_by('prenoms')
    elif sort == 'date':
        patients = Patient.objects.all().order_by('-created_at')
    else:
        patients = Patient.objects.all()

    return render(request, 'doctor/liste_patients.html', {'patients': patients})


def details_patient(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, "Patient non trouvé.")
        return redirect('liste_patients')

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations du patient mises à jour avec succès.")
            return redirect('liste_patients')
    else:
        form = PatientForm(instance=patient)

    return render(request, 'doctor/details_patient.html', {'form': form, 'patient': patient})



def modifier_patient(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, "Patient non trouvé.")
        return redirect('liste_patients')

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations du patient mises à jour avec succès.")
            return redirect('liste_patients')
    else:
        form = PatientForm(instance=patient)

    return render(request, 'doctor/modifier_patient.html', {'form': form, 'patient': patient})




def supprimer_patient(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, "Patient non trouvé.")
        return redirect('liste_patients')

    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Patient supprimé avec succès.")
        return redirect('liste_patients')

    return render(request, 'doctor/supprimer_patient.html', {'patient': patient})



@login_required
def tableau_de_bord(request):
    user = request.user
    is_medecin = Medecin.objects.filter(user=user).exists()
    is_admin = user.is_superuser  

    context = {
        'is_medecin': is_medecin,
        'is_admin': is_admin,
    }

    # Bloc pour les médecins
    if is_medecin:
        total_patients = Patient.objects.count()
        rdv_du_jour = RendezVous.objects.filter(date=date.today()).count()
        alertes = Patient.objects.filter(alerte_medicale=True).count()
        consultations_mois = Consultation.objects.filter(
            date__month=now().month,
            date__year=now().year
        ).count()
        dossiers_recents = Consultation.objects.select_related('patient').order_by('-date')[:5]

        context.update({
            'total_patients': total_patients,
            'rdv_du_jour': rdv_du_jour,
            'alertes': alertes,
            'consultations_mois': consultations_mois,
            'dossiers_recents': dossiers_recents,
        })

    # Bloc pour les administrateurs
    if is_admin:
        print("=== ADMIN CONNECTÉ ===")
        print(request.user, request.user.is_authenticated)

        total_medecins = Medecin.objects.count()
        medecins_recents = Medecin.objects.filter(user__isnull=False)\
                                .select_related('user')\
                                .order_by('-id')[:8]
        fonctionnalites = Fonctionnalite.objects.all()  
        print("Fonctionnalités récupérées :", fonctionnalites)

        context.update({
            'total_medecins': total_medecins,
            'medecins_recents': medecins_recents,
            'fonctionnalites': fonctionnalites,  
        })

    return render(request, 'index.html', context)



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
            return redirect('index')
    else:
        form = DoctorProfileForm(instance=doctor, user=request.user)
    return render(request, 'doctor/mon_profil.html', {'form': form})

@login_required
def supprimer_avatar(request):
    medecin = Medecin.objects.get(user=request.user)
    if medecin.photo_profil:
        medecin.photo_profil.delete(save=True)
        messages.success(request, "Photo de profil supprimée avec succès.")
    return redirect('index')



def liste_medecins(request):
    medecins = Medecin.objects.select_related('user').all()
    return render(request, 'admin/liste_medecins.html', {'medecins': medecins})


@staff_member_required
def ajouter_medecin(request):
    if request.method == 'POST':
        form = MedecinCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Création du compte utilisateur
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            nom = form.cleaned_data['nom']
            prenoms = form.cleaned_data['prenoms']

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=nom,
                last_name=prenoms
            )

            # Création du médecin lié à l'utilisateur
            medecin = form.save(commit=False)
            medecin.user = user
            medecin.save()

            # ✅ Envoi de l'e-mail de bienvenue
            subject = 'Création de votre compte Médecin'
            message = (
                f"Bonjour {prenoms},\n\n"
                f"Votre compte a été créé avec succès.\n\n"
                f"Identifiant : {username}\n"
                f"Mot de passe : {password}\n\n"
                f"⚠️ Vous pouvez changer votre mot de passe à tout moment depuis votre tableau de bord.\n\n"
                f"Merci de votre confiance !"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        

            messages.success(request, "Médecin ajouté avec succès et email envoyé.")
            return redirect('liste_medecins')
        else:
            messages.error(request, "Erreur lors de la validation du formulaire.")
    else:
        form = MedecinCreationForm()
    
    return render(request, 'admin/ajouter_medecin.html', {'form': form})


def gestion_medecins(request):
    medecins = Medecin.objects.all()
    return render(request, 'admin/gestion_medecins.html', {'medecins': medecins})




def modifier_medecin(request, medecin_id):
    medecin = get_object_or_404(Medecin, id=medecin_id)
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=medecin, user=medecin.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Médecin modifié avec succès.")
            return redirect('liste_medecins')
    else:
        form = DoctorProfileForm(instance=medecin, user=medecin.user)
    return render(request, 'admin/modifier_medecin.html', {'form': form, 'medecin': medecin})


def supprimer_medecin(request, medecin_id):
    medecin = get_object_or_404(Medecin, id=medecin_id)
    if request.method == 'POST':
        if medecin.user:
            medecin.user.delete()  # supprime le médecin ET l'utilisateur lié
        else:
            medecin.delete()
        messages.success(request, "Médecin supprimé avec succès.")
        return redirect('liste_medecins')
    return render(request, 'admin/supprimer_medecin.html', {'medecin': medecin})




def rechercher_medecin(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenoms = request.POST.get('prenoms')
        medecins = Medecin.objects.filter(nom__icontains=nom, prenoms__icontains=prenoms)
        return render(request, 'admin/liste_medecins.html', {'medecins': medecins})
    return render(request, 'admin/rechercher_medecin.html')



def export_rapport_pdf(request):
    consultations = Consultation.objects.filter(
        date__month=timezone.now().month,
        date__year=timezone.now().year
    )

    # chemin absolu du logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.jpg')
    logo_base64 = get_image_base64(logo_path)

    context = {
        'consultations': consultations,
        'logo_base64': logo_base64,
        'date_export': datetime.now()
    }

    template = render_to_string('doctor/rapport_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_consultations.pdf"'

    pisa.CreatePDF(template, dest=response)
    return response

@login_required
@staff_member_required
def exporter_medecins_pdf(request):
    medecins = Medecin.objects.select_related('user').all()
    template = get_template('admin/rapport_medecins.html')
    html = template.render({'medecins': medecins})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_medecins.pdf"'

    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=response, encoding='UTF-8')
    return response


@login_required
def ajouter_antecedent(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = AntecedentForm(request.POST)
        if form.is_valid():
            antecedent = form.save(commit=False)
            antecedent.patient = patient
            antecedent.medecin = request.user
            antecedent.save()
            messages.success(request, "Antécédent ajouté avec succès.")
            return redirect('details_patient', patient_id=patient.id)
    else:
        form = AntecedentForm()

    return render(request, 'doctor/ajouter_antecedent.html', {
        'form': form,
        'patient': patient,
    })


@login_required
def modifier_antecedent(request, antecedent_id):
    antecedent = get_object_or_404(Antecedent, id=antecedent_id)
    patient = antecedent.patient

    if request.method == "POST":
        form = AntecedentForm(request.POST, instance=antecedent)
        if form.is_valid():
            form.save()
            return redirect('details_patient', patient.id)
    else:
        form = AntecedentForm(instance=antecedent)

    return render(request, "doctor/modifier_antecedent.html", {
        "form": form,
        "patient": patient,
        "antecedent": antecedent,
    })


@login_required
def supprimer_antecedent(request, antecedent_id):
    antecedent = get_object_or_404(Antecedent, id=antecedent_id)
    patient_id = antecedent.patient.id

    if request.method == "POST":
        antecedent.delete()
        return redirect('details_patient', patient_id)

    return render(request, "doctor/confirmer_supprimer_antecedent.html", {
        "antecedent": antecedent,
        "patient_id": patient_id,
    })


@login_required
def ajouter_prescription(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # Formset classique pour les médicaments
    MedicamentFormSet = formset_factory(MedicamentPrescritForm, extra=1, can_delete=True)

    if request.method == 'POST':
        prescription_form = PrescriptionForm(request.POST)
        medicament_formset = MedicamentFormSet(request.POST)

        if prescription_form.is_valid() and medicament_formset.is_valid():
            # Sauvegarde de la prescription
            prescription = prescription_form.save(commit=False)
            prescription.patient = patient
            prescription.medecin = request.user
            prescription.save()

            # Sauvegarde des médicaments
            for form in medicament_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    medicament = form.save(commit=False)
                    medicament.prescription = prescription
                    medicament.save()

            return redirect('details_patient', patient.id)

    else:
        prescription_form = PrescriptionForm()
        medicament_formset = MedicamentFormSet()  # formulaire vide à l'ouverture

    # Récupération des antécédents critiques pour affichage
    antecedents_critiques = patient.antecedents.filter(important=True)

    return render(request, "doctor/ajout_prescription.html", {
        "patient": patient,
        "prescription_form": prescription_form,
        "medicament_formset": medicament_formset,
        "antecedents_critiques": antecedents_critiques,
    })

@login_required
def renouveler_prescription(request, prescription_id):
    ancienne_prescription = get_object_or_404(Prescription, id=prescription_id)
    patient = ancienne_prescription.patient

    if request.method == 'POST':
        nouvelle_prescription = Prescription.objects.create(
            patient=patient,
            medecin=request.user,
            remarques=ancienne_prescription.remarques
        )

        for medicament in ancienne_prescription.medicaments.all():
            MedicamentPrescrit.objects.create(
                prescription=nouvelle_prescription,
                nom_medicament=medicament.nom_medicament,
                posologie=medicament.posologie,
                duree_traitement=medicament.duree_traitement
            )

        return redirect('details_patient', patient.id)

    return render(request, 'doctor/renouveler_prescription_confirm.html', {
        'ancienne_prescription': ancienne_prescription
    })



@login_required
def supprimer_prescription(request, id):
    prescription = get_object_or_404(Prescription, id=id)
    patient_id = prescription.patient.id
    if request.method == 'POST':
        prescription.delete()
        messages.success(request, "Prescription supprimée avec succès.")
    return redirect('details_patient', patient_id)


@login_required
def modifier_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    patient = prescription.patient
    antecedents_critiques = patient.antecedents.filter(important=True)

    # Formset pour les médicaments existants
    MedicamentFormSet = modelformset_factory(
        MedicamentPrescrit,
        form=MedicamentPrescritForm,
        extra=1,          # Permet d'ajouter un nouveau médicament
        can_delete=True   # Permet de supprimer un médicament
    )

    if request.method == 'POST':
        prescription_form = PrescriptionForm(request.POST, instance=prescription)
        medicament_formset = MedicamentFormSet(
            request.POST,
            queryset=prescription.medicaments.all()
        )

        if prescription_form.is_valid() and medicament_formset.is_valid():
            # Enregistrer la prescription
            prescription_form.save()

            # Enregistrer ou supprimer les médicaments
            for form in medicament_formset:
                if form.cleaned_data:
                    if form.cleaned_data.get('DELETE'):
                        if form.instance.pk:
                            form.instance.delete()
                    else:
                        medicament = form.save(commit=False)
                        medicament.prescription = prescription
                        medicament.save()

            return redirect('details_patient', patient.id)
        else:
            # Debug des erreurs
            print(prescription_form.errors)
            print(medicament_formset.errors)

    else:
        prescription_form = PrescriptionForm(instance=prescription)
        medicament_formset = MedicamentFormSet(queryset=prescription.medicaments.all())

    return render(request, 'doctor/modifier_prescription.html', {
        'prescription_form': prescription_form,
        'medicament_formset': medicament_formset,
        'patient': patient,
        'prescription': prescription,
        'antecedents_critiques': antecedents_critiques,
    })
