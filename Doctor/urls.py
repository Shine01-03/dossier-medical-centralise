from django.urls import path
from . import views
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .views import ajouter_antecedent



urlpatterns = [
    path('', views.home, name='home'),

    path('dashboard/', views.index, name='index'),

    path('statistiques/donnees/', views.statistiques_donnees, name='statistiques_donnees'),

    path('rendezvous/details/', views.details_rendezvous, name='details_rendezvous'),
    path('exporter-medecins/', views.exporter_medecins_pdf, name='exporter_medecins'),

   
    # Url du patient

    path('patients/ajouter/', views.ajouter_patient, name='ajouter_patient'),
    path('patients/liste/', views.liste_patients, name='liste_patients'),
    path('details/<int:patient_id>/', views.details_patient, name='details_patient'),
    path('modifier/<int:patient_id>/', views.modifier_patient, name='modifier_patient'),
    path('supprimer/<int:patient_id>/', views.supprimer_patient, name='supprimer_patient'),
    path('patients/<int:patient_id>/ajouter_antecedent/', ajouter_antecedent, name='ajouter_antecedent'),
    path('patients/<int:patient_id>/ajouter_prescription/', views.ajouter_prescription, name='ajouter_prescription'),
    path('prescriptions/<int:id>/supprimer/', views.supprimer_prescription, name='supprimer_prescription'),
    path('prescription/<int:prescription_id>/renouveler/', views.renouveler_prescription, name='renouveler_prescription'),
    path('prescription/<int:prescription_id>/modifier/', views.modifier_prescription, name='modifier_prescription'),
    path('antecedent/<int:antecedent_id>/modifier/', views.modifier_antecedent, name='modifier_antecedent'),
    path('antecedent/<int:antecedent_id>/supprimer/', views.supprimer_antecedent, name='supprimer_antecedent'),





    # url de connexion et de deconnexion
    path('login/', views.connexion, name='login'),
    path('logout/', views.deconnexion, name='logout'),
    path('profil/supprimer-avatar/', views.supprimer_avatar, name='supprimer_avatar'),


    #url pour médecin
    path('gestion-medecins/', views.gestion_medecins, name='gestion_medecins'),
    path('ajouter_medecin/', views.ajouter_medecin, name='ajouter_medecin'),
    path('medecins/modifier/<int:medecin_id>/', views.modifier_medecin, name='modifier_medecin'),
    path('medecins/supprimer/<int:medecin_id>/', views.supprimer_medecin, name='supprimer_medecin'),
    path('liste_medecins/', views.liste_medecins, name='liste_medecins'),
    path('exporter-rapport/', views.export_rapport_pdf, name='export_rapport_pdf'),


    path('profil/', views.mon_profil, name='mon_profil'),
    
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='doctor/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='doctor/password_change_done.html'), name='password_change_done'),


]



    
