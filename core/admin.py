from django.contrib import admin
from .models import Clinica, PerfilUsuario, Paciente, Tratamiento, Cita

# 1. Administrar las Clínicas
@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'creado_en')
    search_fields = ('nombre',)

# 2. Administrar los Usuarios (Ex-Kinesiólogos)
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'clinica', 'es_administrador')
    list_filter = ('clinica',)

# 3. Administrar Pacientes (Con filtro por clínica)
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'clinica')
    list_filter = ('clinica',) # ¡Vital para el SaaS!
    search_fields = ('nombre', 'rut')

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'clinica')
    list_filter = ('clinica',)

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha', 'hora', 'estado', 'clinica')
    list_filter = ('clinica', 'fecha', 'estado')