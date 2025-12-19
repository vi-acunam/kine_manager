from django import forms

from .models import Paciente # <--- Asegúrate de importar el modelo

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        # Aquí definimos QUÉ campos mostrar y en qué ORDEN
        fields = [
            'nombre', 'rut', 'fecha_nacimiento', 
            'telefono', 'email', 'direccion', 
            'ocupacion', 'deporte', 
            'diagnostico_ingreso', 'antecedentes'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), # Calendario
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion': forms.TextInput(attrs={'class': 'form-control'}),
            'deporte': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Textarea hace que el cuadro sea más grande (para escribir párrafos)
            'diagnostico_ingreso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'antecedentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RegistroSaaSForm(forms.Form):
    username = forms.CharField(label="Nombre de Usuario", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nombre_clinica = forms.CharField(label="Nombre de tu Centro/Clínica", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
