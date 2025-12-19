from django.urls import path
from .views import registro_saas, lista_pacientes, detalle_paciente, redireccion_home

urlpatterns = [
    path('', redireccion_home, name='home'),
    path('pacientes/', lista_pacientes, name='lista_pacientes'),
    path('registro/', registro_saas, name='registro'),
    # NUEVA LÍNEA: <int:paciente_id> captura el número (1, 2, 50, etc.)
    path('pacientes/<int:paciente_id>/', detalle_paciente, name='detalle_paciente'),
]