from .models import Medecin

def role_utilisateur(request):
    is_medecin = False
    if request.user.is_authenticated:
        is_medecin = Medecin.objects.filter(user=request.user).exists()
    return {'is_medecin': is_medecin}


def medecin_context(request):
    if request.user.is_authenticated:
        try:
            medecin = Medecin.objects.get(user=request.user)
            return {'medecin': medecin}
        except Medecin.DoesNotExist:
            return {}
    return {}