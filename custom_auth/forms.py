from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Quiz

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']

class EditProfileForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'bio', 'avatar']