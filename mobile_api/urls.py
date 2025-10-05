from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet, basename='patient')






urlpatterns = [
    path('patients/<str:matricule>/antecedents/', views.get_antecedents_by_patient),    
    path('', include(router.urls)),
    path('register/', views.register_patient, name='register_patient'),
    path('login/', views.login_patient, name='login_patient'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path("mes_antecedents/", views.mes_antecedents, name="mes_antecedents"),
    path("mes_prescriptions/", views.mes_prescriptions, name="mes_prescriptions"),
    path("medecins/", views.liste_medecins, name="liste_medecins"),
    path("rendezvous/demander/", views.demander_rendezvous, name="demander_rendezvous"),
    path("rendezvous/medecin/", views.liste_rendezvous_medecin, name="liste_rendezvous_medecin"),
    path("rendezvous/patient/", views.liste_rendezvous_patient, name="liste_rendezvous_patient"),
    path("rendezvous/<int:rdv_id>/statut/", views.changer_statut_rendezvous, name="changer_statut_rendezvous"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    
    ]
