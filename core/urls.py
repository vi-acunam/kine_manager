from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. Ruta inteligente: Si entras a la raíz, decide si vas al login o a la app
    path('', views.redireccion_home, name='home'),

    # 2. El Login (Usamos la vista nativa de Django pero con nuestro HTML)
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    
    # 3. El Logout (Cerrar sesión)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 4. Registro (La que creamos en el mensaje anterior)
    path('registro/', views.registro_saas, name='registro'),

    # 5. La App
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
]