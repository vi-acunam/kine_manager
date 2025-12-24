from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('pacientes/<int:paciente_id>/agendar/', views.agendar_cita, name='agendar_cita'),
    path('cita/<int:cita_id>/cambiar_estado/<str:nuevo_estado>/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
    path('cita/<int:cita_id>/sala/', views.modo_consulta, name='modo_consulta'),
    path('cita/<int:cita_id>/evolucion/', views.editar_evolucion, name='editar_evolucion'),
    path('calendario/', views.ver_calendario, name='ver_calendario'),

# Ruta oculta que entrega los datos en JSON
    path('api/citas/', views.listar_citas_json, name='listar_citas_json'),
    path('cita/<int:cita_id>/pagar/', views.registrar_pago, name='registrar_pago'),
    path('tratamientos/nuevo/', views.crear_tratamiento, name='crear_tratamiento'),
    path('equipo/nuevo/', views.crear_staff, name='crear_staff'),
    path('dashboard/', views.dashboard_analitica, name='dashboard'),
    path('pacientes/<int:paciente_id>/pdf/', views.generar_pdf_paciente, name='generar_pdf_paciente'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),
    path('configuracion/', views.configuracion_clinica, name='configuracion_clinica'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

