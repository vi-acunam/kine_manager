# Asegúrate de importar get_object_or_404
from django.shortcuts import render, get_object_or_404
from .models import Paciente
from django.shortcuts import redirect

def lista_pacientes(request):
    pacientes = Paciente.objects.all().order_by('-id')
    return render(request, 'core/lista_pacientes.html', {'pacientes': pacientes})

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