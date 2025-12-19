from django import forms

from .models import Paciente # <--- Asegúrate de importar el modelo

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        # OJO: No incluimos 'clinica' aquí para que el usuario no la toque
        fields = ['nombre', 'rut', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RegistroSaaSForm(forms.Form):
    username = forms.CharField(label="Nombre de Usuario", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nombre_clinica = forms.CharField(label="Nombre de tu Centro/Clínica", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
