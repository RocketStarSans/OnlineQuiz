from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

# 1. Реєстрація
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'OnlineQuiz/register.html', {'form': form})

# 2. Вхід
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'OnlineQuiz/login.html', {'form': form})

# 3. Вихід
def logout_view(request):
    logout(request)
    return redirect('index')

def index_view(request):
    return render(request, 'OnlineQuiz/index.html')