# Asegúrate de importar get_object_or_404
from django.shortcuts import render, get_object_or_404
from .models import Paciente, Cita, Tratamiento
from django.shortcuts import redirect
from django.db.models import Sum
from datetime import date

def lista_pacientes(request):
    pacientes = Paciente.objects.all().order_by('-id')
    
    # --- LÓGICA DE CAJA ---
    hoy = date.today()
    
    # Sumamos el precio de los tratamientos de las citas de HOY
    # (Solo sumamos si la cita NO está anulada)
    caja_hoy = Cita.objects.filter(
        fecha_hora__date=hoy
    ).exclude(estado='ANULADA').aggregate(Sum('tratamiento__precio'))
    
    # Si no hay ventas, el resultado es None, así que lo convertimos a 0
    total_recaudado = caja_hoy['tratamiento__precio__sum'] or 0

    context = {
        'pacientes': pacientes,
        'total_recaudado': total_recaudado, # Enviamos el dato al HTML
        'fecha_hoy': hoy
    }
    return render(request, 'core/lista_pacientes.html', context)

# --- NUEVA FUNCIÓN ---
def detalle_paciente(request, paciente_id):
    # 1. Buscamos al paciente por su ID
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # 2. Buscamos sus citas (usamos 'citas' porque definimos related_name='citas' en el modelo)
    # Las ordenamos por fecha (de la más reciente a la más antigua)
    historial = paciente.citas.all().order_by('-fecha_hora')
    
    context = {
        'paciente': paciente,
        'historial': historial
    }
    return render(request, 'core/detalle_paciente.html', context)

def redireccion_home(request):
    return redirect('lista_pacientes')