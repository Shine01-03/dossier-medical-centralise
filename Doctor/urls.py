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
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
]



    
