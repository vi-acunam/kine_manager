from django.db import models
from django.contrib.auth.models import User

# 1. EL "TENANT" (La Clínica/Cliente que te paga)
class Clinica(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# 2. EXTENSIÓN DEL USUARIO (Para saber a qué clínica pertenece el Kine)
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    es_administrador = models.BooleanField(default=False) # ¿Es el dueño de la clínica?

    def __str__(self):
        return f"{self.usuario.username} - {self.clinica.nombre}"

# 3. MODELOS DE NEGOCIO (Todos deben tener un "padre" Clínica)
class Paciente(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE) # <--- OBLIGATORIO
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    telefono = models.CharField(max_length=20, blank=True)
    
    class Meta:
        # El RUT no puede repetirse DENTRO de la misma clínica, pero sí en otras
        unique_together = ['clinica', 'rut']

    def __str__(self):
        return f"{self.nombre} ({self.clinica.nombre})"

class Tratamiento(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Cita(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE, null=True)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, default='AGENDADA')