from django.db import models
from django.contrib.auth.models import User

# Opciones para listas desplegables
ESTADOS_CITA = [
    ('AGENDADA', 'Agendada'),
    ('CONFIRMADA', 'Confirmada'),
    ('EN_ATENCION', 'En Atención'),
    ('FINALIZADA', 'Finalizada'),
    ('ANULADA', 'Anulada'),
]

class Paciente(models.Model):
    rut = models.CharField(max_length=12, unique=True, help_text="RUT o DNI")
    nombre_completo = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    antecedentes_medicos = models.TextField(blank=True, help_text="Cirugías, alergias, enfermedades crónicas")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    direccion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dirección")
    ocupacion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ocupación")
    institucion = models.CharField(max_length=100, blank=True, null=True, help_text="Isapre, Fonasa, Club, etc.")
    deporte = models.CharField(max_length=100, blank=True, null=True, help_text="Deporte que practica")
    diagnostico_ingreso = models.CharField(max_length=200, blank=True, null=True, verbose_name="Diagnóstico Médico/Ingreso")

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"

class Kinesiologo(models.Model):
    # Vinculamos al sistema de usuarios de Django para que pueda loguearse
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100, default="Kinesiología General")
    registro_profesional = models.CharField(max_length=50, help_text="Nro de registro superintendencia")

    def __str__(self):
        return self.usuario.get_full_name()

class Tratamiento(models.Model):
    """Ej: Pack 10 Sesiones Kinesioterapia, Evaluación, Punción Seca"""
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=0) # decimal_places=0 para pesos (CLP/COP)
    sesiones_totales = models.PositiveIntegerField(default=1, help_text="Cantidad de sesiones que incluye este pack")

    def __str__(self):
        return self.nombre

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    kinesiologo = models.ForeignKey(Kinesiologo, on_delete=models.SET_NULL, null=True)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_CITA, default='AGENDADA')
    
    # Control de sesiones (Ej: Sesión 1 de 10)
    numero_sesion = models.PositiveIntegerField(default=1, help_text="Número de sesión actual")
    
    def __str__(self):
        return f"{self.fecha_hora} - {self.paciente}"

class FichaEvolucion(models.Model):
    """La parte clínica: se llena DESPUÉS o DURANTE la cita"""
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    motivo_consulta = models.CharField(max_length=200)
    
    # Formato SOAP (Subjetivo, Objetivo, Análisis, Plan)
    subjetivo = models.TextField(help_text="Lo que relata el paciente (dolor, sensaciones)")
    objetivo = models.TextField(help_text="Hallazgos físicos, rangos de movimiento, fuerza")
    
    # Datos Cuantitativos (Clave para gráficos de evolución)
    nivel_dolor_eva = models.PositiveIntegerField(help_text="Escala 1 a 10", choices=[(i, i) for i in range(11)])
    
    analisis_plan = models.TextField(help_text="Diagnóstico kinesiológico y ejercicios para la casa")
    proxima_sesion_sugerida = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Evolución: {self.cita}"