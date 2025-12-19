from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Portada y Accesos
    path('', views.redireccion_home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro_saas, name='registro'),

    # Pacientes
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),

    # --- RUTAS NUEVAS (Las que faltaban) ---
    path('tratamientos/nuevo/', views.crear_tratamiento, name='crear_tratamiento'),
    path('equipo/nuevo/', views.crear_staff, name='crear_staff'),
]