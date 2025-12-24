from django import forms

from .models import Paciente # <--- Asegúrate de importar el modelo

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        # Aquí definimos QUÉ campos mostrar y en qué ORDEN
        fields = ['nombre', 'rut', 'fecha_nacimiento', 'telefono', 'email', 'direccion', 
                  'prevision', 'detalle_prevision', 'ocupacion', 'deporte', 
                  'diagnostico_ingreso', 'antecedentes']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), # Calendario
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion': forms.TextInput(attrs={'class': 'form-control'}),
            'deporte': forms.TextInput(attrs={'class': 'form-control'}),
            'prevision': forms.Select(attrs={'class': 'form-select', 'id': 'select-prevision'}),
            'detalle_prevision': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'input-detalle',
                'placeholder': 'Ej: Dipreca, Capredena, Seguro Escolar...'
            }),
            # Textarea hace que el cuadro sea más grande (para escribir párrafos)
            'diagnostico_ingreso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'antecedentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RegistroSaaSForm(forms.Form):
    username = forms.CharField(label="Nombre de Usuario", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nombre_clinica = forms.CharField(label="Nombre de tu Centro/Clínica", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

from .models import Tratamiento

class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['nombre', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sesión Kinesiología'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 35000'}),
        }

class StaffForm(forms.Form):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nombre_completo = forms.CharField(label="Nombre Real", widget=forms.TextInput(attrs={'class': 'form-control'}))

from .models import Cita # Asegúrate de importar Cita arriba

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'hora', 'tratamiento'] # No pedimos paciente ni clínica
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'tratamiento': forms.Select(attrs={'class': 'form-select'}),
        }

class EvolucionForm(forms.ModelForm):
    class Meta:
        model = Cita  # <--- Usamos el modelo Cita, pero solo editamos un campo
        fields = ['evolucion']
        widgets = {
            'evolucion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5, 
                'placeholder': 'Describa la evolución del paciente, dolor EVA, ejercicios realizados...'
            }),
        }

from .models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'metodo']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monto a pagar'}),
            'metodo': forms.Select(attrs={'class': 'form-select'}),
        }

from .models import Clinica

class ClinicaForm(forms.ModelForm):
    class Meta:
        model = Clinica
        fields = ['nombre', 'direccion', 'logo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Siempre Viva 123'}),
            # El input de archivo no necesita mucha clase, pero podemos ponerle form-control
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }