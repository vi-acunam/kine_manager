from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from .models import Paciente, Cita, Tratamiento
from .forms import RegistroSaaSForm

# --- FUNCIÓN AUXILIAR (La clave del SaaS) ---
def obtener_clinica_usuario(user):
    """
    Intenta obtener la clínica asociada al usuario logueado.
    Si es un superusuario antiguo sin perfil, podría dar error,
    así que manejamos la excepción.
    """
    try:
        return user.perfil.clinica
    except AttributeError:
        # Esto pasa si el usuario (ej: admin) no tiene creado su 'PerfilUsuario'
        return None

# --- VISTAS ---

def redireccion_home(request):
    """
    Si el usuario ya entró -> Mándalo directo a sus pacientes.
    Si no ha entrado -> Mándalo al Login.
    """
    if request.user.is_authenticated:
        return redirect('lista_pacientes')
    else:
        return redirect('login')

@login_required
def lista_pacientes(request):
    # 1. Identificar la clínica del usuario
    mi_clinica = obtener_clinica_usuario(request.user)
    
    # Seguridad: Si el usuario no tiene clínica asignada, no mostramos nada
    if not mi_clinica:
        return render(request, 'core/error.html', {
            'mensaje': 'Tu usuario no tiene una clínica asignada. Contacta al soporte.'
        })

    # 2. FILTRO SAAS: Solo traemos pacientes de ESTA clínica
    pacientes = Paciente.objects.filter(clinica=mi_clinica).order_by('-id')

    # 3. LÓGICA FINANCIERA (Caja Diaria)
    hoy = date.today()
    
    # Sumamos el precio de los tratamientos de las citas de HOY
    # Filtramos por clínica + fecha + estado (no anulada)
    caja_hoy = Cita.objects.filter(
        clinica=mi_clinica,
        fecha=hoy
    ).exclude(estado='ANULADA').aggregate(Sum('tratamiento__precio'))

    # Si la suma es None (no hay citas), la convertimos a 0
    total_recaudado = caja_hoy['tratamiento__precio__sum'] or 0

    context = {
        'pacientes': pacientes,
        'total_recaudado': total_recaudado,
        'fecha_hoy': hoy,
        'nombre_clinica': mi_clinica.nombre # Para mostrarlo en el título si quieres
    }
    return render(request, 'core/lista_pacientes.html', context)

@login_required
def detalle_paciente(request, paciente_id):
    mi_clinica = obtener_clinica_usuario(request.user)

    # SEGURIDAD SAAS:
    # Usamos get_object_or_404 buscando por ID y también por CLÍNICA.
    # Si alguien intenta cambiar el ID en la URL para ver un paciente de otra clínica,
    # le saldrá Error 404 (No encontrado) en lugar de mostrar datos ajenos.
    paciente = get_object_or_404(Paciente, id=paciente_id, clinica=mi_clinica)

    # Historial de citas (también filtrado implícitamente porque el paciente ya es de la clínica)
    historial = Cita.objects.filter(paciente=paciente).order_by('-fecha', '-hora')

    context = {
        'paciente': paciente,
        'historial': historial
    }
    return render(request, 'core/detalle_paciente.html', context)

def registro_saas(request):
    if request.method == 'POST':
        form = RegistroSaaSForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # PASO A: Crear la Clínica
            nueva_clinica = Clinica.objects.create(
                nombre=data['nombre_clinica'],
                direccion="Dirección pendiente"
            )
            
            # PASO B: Crear el Usuario
            nuevo_usuario = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            # PASO C: Vincularlos (SaaS)
            PerfilUsuario.objects.create(
                usuario=nuevo_usuario,
                clinica=nueva_clinica,
                es_administrador=True # Es el dueño porque él la creó
            )
            
            # PASO D: Iniciar sesión automáticamente y redirigir
            login(request, nuevo_usuario)
            return redirect('lista_pacientes')
            
    else:
        form = RegistroSaaSForm()

    return render(request, 'core/registro.html', {'form': form})