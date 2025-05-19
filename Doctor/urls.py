from django.urls import path
from . import views
from django.urls import path, include


urlpatterns = [
    path('dashboard/', views.index, name='index'),

    path('statistiques/donnees/', views.statistiques_donnees, name='statistiques_donnees'),

    path('rendezvous/details/', views.details_rendezvous, name='details_rendezvous'),
   
        # Enregistrer le patient dans la base de données

    path('patients/ajouter/', views.ajouter_patient, name='ajouter_patient'),

    # url de connexion et de deconnexion
    path('login/', views.login, name='login'),
    path('deconnexion/', views.deconnexion, name='logout'),

    #url pour ajouter un médecin
     path('gestion-medecins/', views.gestion_medecins, name='gestion_medecins'),
    path('ajouter_medecin/', views.ajouter_medecin, name='ajouter_medecin'),
    path('modifier/<int:medecin_id>/', views.modifier_medecin, name='modifier_medecin'),
    path('supprimer/<int:medecin_id>/', views.supprimer_medecin, name='supprimer_medecin'),
    path('liste_medecins/', views.liste_medecins, name='liste_medecins'),

]



    
