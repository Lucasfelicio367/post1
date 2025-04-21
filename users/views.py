from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.decorators import login_required

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('local:index'))



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_approved:
                login(request, user)
                return HttpResponseRedirect(reverse('local:index'))
            else:
                return render(request, 'users/login.html', {'error': 'Conta não aprovada. Aguarde aprovação do administrador.'})
        else:
            return render(request, 'users/login.html', {'error': 'Credenciais inválidas.'})
    return render(request, 'users/login.html')



def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('local:index'))

    if request.method != "POST":
        form = CustomUserCreationForm()
    else:
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_approved = False  # Não aprovado por padrão
            new_user.save()
            return render(request, 'users/register_success.html')

    context = {'form': form}
    return render(request, 'users/register.html', context)