from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from Doctor.models import Patient, Antecedent, Prescription, RendezVous
from .serializers import PatientSerializer, RegisterPatientSerializer, LoginPatientSerializer, AntecedentSerializer, PrescriptionSerializer, RendezVousSerializer, MedecinSerializer
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from datetime import date as date_cls, time as time_cls, datetime
from django.contrib.auth.models import User

# Create your views here.

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'matricule' 


@api_view(['GET'])
def get_antecedents_by_patient(request, matricule):
    try:
        patient = get_object_or_404(Patient, matricule=matricule)
    except Patient.DoesNotExist:
        return Response({"error": "Patient non trouvé"}, status=404)

    antecedents = Antecedent.objects.filter(patient=patient)
    data = [
        {
            "maladie": ant.maladie,
            "date_diagnostic": ant.date_diagnostic,
            "traitement": ant.traitement
        }
        for ant in antecedents
    ]
    return Response({
        "patient": f"{patient.nom} {patient.prenom}",
        "antecedents": data
    })    




@api_view(['POST'])
def register_patient(request):
    serializer = RegisterPatientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Patient créé avec succès'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login_patient(request):
    serializer = LoginPatientSerializer(data=request.data)
    if serializer.is_valid():
        try:
            patient = Patient.objects.get(email=serializer.validated_data['email'])
        except Patient.DoesNotExist:
            return Response({'error': 'Email ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(serializer.validated_data['password'], patient.password):
            return Response({'error': 'Email ou mot de passe incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        # Génération du token JWT
        refresh = RefreshToken.for_user(patient)
        return Response({
            'message': 'Connexion réussie',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    patient = request.user  # Avec JWT, request.user sera le patient connecté

    if request.method == 'GET':
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_antecedents(request):
    patient = request.user
    antecedents = Antecedent.objects.filter(patient=patient).order_by('-date')
    serializer = AntecedentSerializer(antecedents, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_antecedents(request):
    patient = request.user.patient  # ✅ ça marche maintenant
    antecedents = Antecedent.objects.filter(patient=patient).order_by('-date')
    serializer = AntecedentSerializer(antecedents, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_prescriptions(request):
    patient = request.user
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescription')
    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)



# 0) Liste des médecins pour que le patient puisse choisir
@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def liste_medecins(request):
    medecins = User.objects.filter(is_staff=True).order_by('first_name', 'last_name', 'username')
    return Response(MedecinSerializer(medecins, many=True).data)


# 1) Patient crée un rendez-vous
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demander_rendezvous(request):
    serializer = RendezVousSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        rdv = serializer.save()
        return Response(RendezVousSerializer(rdv).data, status=201)
    return Response(serializer.errors, status=400)



# 2) Médecin consulte ses rendez-vous
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_rendezvous_medecin(request):
    if not getattr(request.user, "is_staff", False):
        return Response({"detail": "Accès réservé aux médecins."}, status=403)
    rdvs = RendezVous.objects.filter(medecin=request.user).order_by('-date', '-heure')
    return Response(RendezVousSerializer(rdvs, many=True).data)

# 2.bis) Patient consulte ses rendez-vous
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_rendezvous_patient(request):
    rdvs = RendezVous.objects.filter(patient=request.user).order_by('-date', '-heure')
    return Response(RendezVousSerializer(rdvs, many=True).data)

# 3) Médecin met à jour le statut
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def changer_statut_rendezvous(request, rdv_id):
    if not getattr(request.user, "is_staff", False):
        return Response({"detail": "Accès réservé aux médecins."}, status=403)
    try:
        rdv = RendezVous.objects.get(id=rdv_id, medecin=request.user)
    except RendezVous.DoesNotExist:
        return Response({"error": "Rendez-vous introuvable"}, status=404)

    nouveau_statut = request.data.get("statut")
    if nouveau_statut not in dict(RendezVous.STATUTS):
        return Response({"error": "Statut invalide"}, status=400)

    rdv.statut = nouveau_statut
    rdv.save()
    return Response({
        "message": f"Statut mis à jour en {nouveau_statut} ✅",
        "rendezvous": RendezVousSerializer(rdv).data
    })