from django.contrib import admin
from .models import Paciente, Kinesiologo, Tratamiento, Cita, FichaEvolucion

# Configuración avanzada para ver mejor las tablas
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'kinesiologo', 'fecha_hora', 'estado', 'numero_sesion')
    list_filter = ('estado', 'fecha_hora', 'kinesiologo')
    search_fields = ('paciente__nombre_completo',)

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'rut', 'telefono')
    search_fields = ('nombre_completo', 'rut')

# Registro simple de los demás
admin.site.register(Kinesiologo)
admin.site.register(Tratamiento)
admin.site.register(FichaEvolucion)