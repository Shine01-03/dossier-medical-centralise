from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connexion automatique après inscription
            return redirect('Accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'Accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('Accounts:dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'Accounts/login.html', {'form': form})

@login_required
def dashboard_view(request):
    if request.user.role == 'medecin':
        return redirect('Doctor:dashboard_medecin') 
    elif request.user.role == 'patient':
        return render(request, 'Accounts/dashboard_patient.html')
    elif request.user.is_superuser:
        return redirect('/admin/')
    
def deconnexion(request):
    logout(request)  
    return redirect('Doctor:index')      
