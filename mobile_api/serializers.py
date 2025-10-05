from rest_framework import serializers
from Doctor.models import Patient, Antecedent, Prescription, RendezVous
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.contrib.auth.models import User

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'nom', 'prenom', 'sexe', 'telephone',
            'date_naissance', 'adresse', 'email',
            'groupe_sanguin', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }


class RegisterPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'nom', 'prenom', 'date_naissance', 'sexe',
            'email', 'password', 'telephone', 'adresse',
            'groupe_sanguin', 'profession', 'situation_matrimoniale',
            'personne_a_prevenir', 'tel_personne_prevenir'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_sexe(self, value):
        """Normalise le sexe."""
        if isinstance(value, str):
            if value.lower() in ['f', 'féminin', 'female']:
                return 'F'
            elif value.lower() in ['m', 'masculin', 'male']:
                return 'M'
        raise serializers.ValidationError("Sexe invalide. Choisir 'M' ou 'F'.")

    def validate_date_naissance(self, value):
        """Accepte plusieurs formats de date et renvoie un objet date."""
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            raise serializers.ValidationError(
                "Format de date invalide. Utilisez YYYY-MM-DD ou DD/MM/YYYY."
            )
        return value

    def create(self, validated_data):
        # Hash le mot de passe
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)



class LoginPatientSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)        



class AntecedentSerializer(serializers.ModelSerializer):
    medecin_nom = serializers.CharField(source="medecin.username", read_only=True)

    class Meta:
        model = Antecedent
        fields = ['id', 'type_antecedent', 'description', 'date', 'important', 'medecin_nom']


class PrescriptionSerializer(serializers.ModelSerializer):
    medecin_nom = serializers.CharField(source="medecin.username", read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'date_prescription', 'remarques', 'medecin_nom']





class MedecinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]



class RendezVousSerializer(serializers.ModelSerializer):
    medecin_nom = serializers.SerializerMethodField()
    patient_nom = serializers.SerializerMethodField()

    class Meta:
        model = RendezVous
        fields = [
            "id", "patient", "medecin", "date", "heure", "motif", "statut",
            "medecin_nom", "patient_nom"
        ]
        read_only_fields = ["patient", "statut"]

    def get_medecin_nom(self, obj):
        if obj.medecin:
            return f"{obj.medecin.first_name} {obj.medecin.last_name}".strip() or obj.medecin.username
        return None

    def get_patient_nom(self, obj):
        try:
            return f"{obj.patient.prenom} {obj.patient.nom}".strip()
        except Exception:
            return str(obj.patient)

    # --- validations personnalisées ---
    def validate(self, data):
        date = data.get("date")
        heure = data.get("heure")
        medecin = data.get("medecin")

        # pas de RDV dans le passé
        from datetime import datetime
        if date and heure:
            if datetime.combine(date, heure) < datetime.now():
                raise serializers.ValidationError("Impossible de prendre un RDV dans le passé.")

        # pas de doublon sur le même créneau pour le même médecin
        if RendezVous.objects.filter(medecin=medecin, date=date, heure=heure).exists():
            raise serializers.ValidationError("Ce créneau est déjà occupé pour ce médecin.")

        return data

    def create(self, validated_data):
        # ici je force le patient depuis le contexte (venant de la vue)
        patient = self.context["request"].user
        validated_data["patient"] = patient
        return super().create(validated_data)
