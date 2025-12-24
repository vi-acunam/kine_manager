from django.db import models
from django.contrib.auth.models import User

# 1. EL "TENANT" (La Clínica/Cliente que te paga)
class Clinica(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, verbose_name="Dirección Comercial")
    # CAMPO NUEVO:
    logo = models.ImageField(upload_to='logos_clinicas/', blank=True, null=True)
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
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    
    # Datos Personales Básicos
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    fecha_nacimiento = models.DateField(null=True, blank=True) # Para calcular la edad
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, verbose_name="Dirección")
    
    # Datos Sociales / Estilo de Vida
    ocupacion = models.CharField(max_length=100, blank=True, default="No especificada", verbose_name="Ocupación")
    deporte = models.CharField(max_length=100, blank=True, default="Sedentario", verbose_name="Deporte/Actividad")
    
    # Datos Clínicos
    diagnostico_ingreso = models.TextField(blank=True, default="En evaluación", verbose_name="Diagnóstico de Ingreso")
    antecedentes = models.TextField(blank=True, default="Sin antecedentes", verbose_name="Antecedentes Médicos")
    
    PREVISION_CHOICES = [
        ('FONASA', 'Fonasa'),
        ('ISAPRE', 'Isapre'),
        ('PARTICULAR', 'Particular'),
        ('OTRO', 'Otro / Convenio'),
    ]

    prevision = models.CharField(max_length=20, choices=PREVISION_CHOICES, default='PARTICULAR', verbose_name="Previsión")

    detalle_prevision = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Especifique Convenio"
    )

    class Meta:
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
    evolucion = models.TextField(blank=True, default='', verbose_name="Evolución Clínica")

    def monto_pagado(self):
        # Suma todos los pagos registrados para esta cita
        total = self.pagos.aggregate(models.Sum('monto'))['monto__sum'] or 0
        return total

    def deuda_pendiente(self):
        if not self.tratamiento:
            return 0
        return self.tratamiento.precio - self.monto_pagado()

    def estado_pago(self):
        deuda = self.deuda_pendiente()
        if deuda <= 0:
            return 'PAGADO'
        elif deuda == self.tratamiento.precio:
            return 'PENDIENTE'
        else:
            return 'PARCIAL'

# --- AL FINAL DE core/models.py ---

class Pago(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='pagos')
    fecha = models.DateField(auto_now_add=True)
    monto = models.IntegerField(verbose_name="Monto Pagado")
    
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('DEBITO', 'Débito/Crédito'),
        ('BONO', 'Bono Fonasa/Isapre'),
    ]
    metodo = models.CharField(max_length=20, choices=METODOS_PAGO, default='EFECTIVO')

    def __str__(self):
        return f"${self.monto} - {self.metodo}"

# --- AHORA VOLVEMOS A LA CLASE CITA (Modifícala) ---
# Busca tu clase Cita y agrégale este método dentro de la clase:

