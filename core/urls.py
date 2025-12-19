from django.urls import path
from . import views

urlpatterns = [
    path('', views.redireccion_home, name='home'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    
    # NUEVA LÍNEA: <int:paciente_id> captura el número (1, 2, 50, etc.)
    path('pacientes/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
]