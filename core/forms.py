from django import forms

class RegistroSaaSForm(forms.Form):
    # 1. Datos del Dueño
    username = forms.CharField(label="Nombre de Usuario", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # 2. Datos de la Clínica
    nombre_clinica = forms.CharField(label="Nombre de tu Centro/Clínica", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))