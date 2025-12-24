from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, datetime
# --- IMPORTACIONES NUEVAS QUE SUELEN FALTAR ---
from django.contrib.auth import login                  # <--- ¿Tienes esta?
from django.contrib.auth.models import User            # <--- ¿Tienes esta?
from .models import Paciente, Cita, Tratamiento, Clinica, PerfilUsuario
from .forms import RegistroSaaSForm
from .forms import PacienteForm # <--- Importa el nuevo form
from django.template.loader import render_to_string
from django.http import HttpResponse
import base64
import os
import mimetypes

@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False) # Pausa la guardada un segundo
            
            # ASIGNACIÓN AUTOMÁTICA SAAS
            # Le asignamos la clínica del usuario que está creando al paciente
            paciente.clinica = obtener_clinica_usuario(request.user)
            
            paciente.save() # Ahora sí guardamos definitivamente
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()

    return render(request, 'core/crear_paciente.html', {'form': form})




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
    
    # Filtramos los PAGOS realizados HOY en MI clínica
    pagos_hoy = Pago.objects.filter(
        cita__clinica=mi_clinica, # Accedemos a la clínica a través de la cita
        fecha=hoy
    ).aggregate(Sum('monto'))

    total_recaudado = pagos_hoy['monto__sum'] or 0

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

from .forms import TratamientoForm # <--- No olvides importarlo arriba

@login_required
def crear_tratamiento(request):
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save(commit=False)
            tratamiento.clinica = obtener_clinica_usuario(request.user) # Asignación SaaS
            tratamiento.save()
            return redirect('lista_pacientes') # O redirigir a una lista de precios
    else:
        form = TratamientoForm()
    
    return render(request, 'core/crear_tratamiento.html', {'form': form})

from .forms import StaffForm # Importar

@login_required
def crear_staff(request):
    # Seguridad: Solo admin puede crear staff
    if not request.user.perfil.es_administrador:
        return redirect('lista_pacientes')

    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # 1. Crear User
            nuevo_kine = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                first_name=data['nombre_completo']
            )
            nuevo_kine.is_staff = True # Dar acceso al admin panel si quieres
            nuevo_kine.save()

            # 2. Vincular a ESTA clínica
            PerfilUsuario.objects.create(
                usuario=nuevo_kine,
                clinica=obtener_clinica_usuario(request.user),
                es_administrador=False 
            )
            return redirect('lista_pacientes')
    else:
        form = StaffForm()

    return render(request, 'core/crear_staff.html', {'form': form})

def cambiar_estado_cita(request, cita_id, nuevo_estado):
    # 1. Seguridad SaaS: Obtenemos la clínica del usuario actual
    mi_clinica = obtener_clinica_usuario(request.user)
    
    if not mi_clinica:
        return redirect('lista_pacientes')

    # 2. Buscamos la cita, pero SOLO si pertenece a MI clínica
    # Esto evita que alguien cambie citas de otra clínica modificando la URL
    cita = get_object_or_404(Cita, id=cita_id, clinica=mi_clinica)

    # 3. Validamos que el estado sea uno de los permitidos
    estados_validos = ['AGENDADA', 'REALIZADA', 'ANULADA']
    
    if nuevo_estado in estados_validos:
        cita.estado = nuevo_estado
        cita.save()
    
    # 4. Volvemos a la ficha del paciente
    return redirect('detalle_paciente', paciente_id=cita.paciente.id)

from .forms import CitaForm # Importar el nuevo form

@login_required
def agendar_cita(request, paciente_id):
    mi_clinica = obtener_clinica_usuario(request.user)
    # Buscamos al paciente asegurando que sea de MI clínica
    paciente = get_object_or_404(Paciente, id=paciente_id, clinica=mi_clinica)

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.paciente = paciente      # Asignamos el paciente de la URL
            cita.clinica = mi_clinica     # Asignamos la clínica del usuario
            cita.estado = 'AGENDADA'
            cita.save()
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        form = CitaForm()

    # Filtramos los tratamientos para mostrar SOLO los de mi clínica
    form.fields['tratamiento'].queryset = Tratamiento.objects.filter(clinica=mi_clinica)

    return render(request, 'core/agendar_cita.html', {'form': form, 'paciente': paciente})

from .forms import EvolucionForm

@login_required
def editar_evolucion(request, cita_id):
    mi_clinica = obtener_clinica_usuario(request.user)
    # Seguridad: Solo editar citas de MI clínica
    cita = get_object_or_404(Cita, id=cita_id, clinica=mi_clinica)

    if request.method == 'POST':
        form = EvolucionForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            # Al guardar, volvemos a la ficha del paciente
            return redirect('detalle_paciente', paciente_id=cita.paciente.id)
    else:
        # Si entramos por primera vez, cargamos el texto que ya existía
        form = EvolucionForm(instance=cita)

    return render(request, 'core/editar_evolucion.html', {'form': form, 'cita': cita})

@login_required
def modo_consulta(request, cita_id):
    mi_clinica = obtener_clinica_usuario(request.user)
    cita_actual = get_object_or_404(Cita, id=cita_id, clinica=mi_clinica)
    paciente = cita_actual.paciente

    # Buscamos las últimas 3 citas ANTERIORES a esta para referencia
    historial_previo = Cita.objects.filter(
        paciente=paciente, 
        fecha__lt=cita_actual.fecha  # Fechas menores a hoy
    ).order_by('-fecha')[:3]

    if request.method == 'POST':
        form = EvolucionForm(request.POST, instance=cita_actual)
        if form.is_valid():
            cita = form.save(commit=False)
            # MAGIA: Al terminar la consulta, asumimos que se realizó
            cita.estado = 'REALIZADA' 
            cita.save()
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        form = EvolucionForm(instance=cita_actual)

    context = {
        'cita': cita_actual,
        'paciente': paciente,
        'form': form,
        'historial_previo': historial_previo
    }
    return render(request, 'core/modo_consulta.html', context)

from django.http import JsonResponse
from datetime import datetime, timedelta

# --- VISTA PARA EL CALENDARIO (HTML) ---
@login_required
def ver_calendario(request):
    return render(request, 'core/calendario.html')

# --- API DE DATOS (JSON) ---
@login_required
def listar_citas_json(request):
    mi_clinica = obtener_clinica_usuario(request.user)
    
    # Traemos todas las citas de la clínica (menos las anuladas si prefieres ocultarlas)
    citas = Cita.objects.filter(clinica=mi_clinica).exclude(estado='ANULADA')
    
    eventos = []
    
    for c in citas:
        # FullCalendar necesita fecha y hora juntas en formato ISO
        fecha_inicio = datetime.combine(c.fecha, c.hora)
        # Asumiremos que cada sesión dura 1 hora (puedes cambiarlo después)
        fecha_fin = fecha_inicio + timedelta(hours=1)
        
        # Definir colores según estado
        color = '#3788d8' # Azul (Default/Agendada)
        if c.estado == 'REALIZADA':
            color = '#28a745' # Verde
        elif c.estado == 'ANULADA':
            color = '#dc3545' # Rojo

        eventos.append({
            'title': f"{c.paciente.nombre} ({c.tratamiento.nombre})",
            'start': fecha_inicio.isoformat(),
            'end': fecha_fin.isoformat(),
            'color': color,
            # Al hacer clic, llevamos al "Modo Consulta" que creamos antes
            'url': f"/cita/{c.id}/sala/" 
        })
        
    return JsonResponse(eventos, safe=False)

from .forms import PagoForm # No olvides importar
from .models import Pago      # No olvides importar

@login_required
def registrar_pago(request, cita_id):
    mi_clinica = obtener_clinica_usuario(request.user)
    cita = get_object_or_404(Cita, id=cita_id, clinica=mi_clinica)

    # Calculamos cuánto le falta por pagar para sugerirlo en el formulario
    deuda = cita.deuda_pendiente()

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.cita = cita
            pago.save()
            return redirect('detalle_paciente', paciente_id=cita.paciente.id)
    else:
        # Pre-llenamos el monto con la deuda total
        form = PagoForm(initial={'monto': deuda})

    return render(request, 'core/registrar_pago.html', {
        'form': form, 
        'cita': cita, 
        'deuda': deuda
    })

from django.db.models import Count, Sum # <--- IMPORTANTE: Agrega esto al inicio del archivo si no está

@login_required
def dashboard_analitica(request):
    mi_clinica = obtener_clinica_usuario(request.user)
    
    # 1. KPI: Ingresos de este mes
    hoy = date.today()
    pagos_mes = Pago.objects.filter(
        cita__clinica=mi_clinica,
        fecha__month=hoy.month,
        fecha__year=hoy.year
    ).aggregate(Sum('monto'))
    ingresos_mes = pagos_mes['monto__sum'] or 0

    # 2. KPI: Deuda Total Histórica (Dinero que está en la calle)
    # Buscamos citas con pago parcial o pendiente y sumamos lo que falta
    # (Nota: Esto es una aproximación, para exactitud total requeriría lógica más compleja, pero sirve para el MVP)
    citas_pendientes = Cita.objects.filter(clinica=mi_clinica).exclude(estado='ANULADA')
    deuda_total = 0
    for c in citas_pendientes:
        deuda_total += c.deuda_pendiente()

    # 3. DATOS PARA GRÁFICO 1: Estado de Citas
    # Esto devuelve algo como: [{'estado': 'REALIZADA', 'total': 50}, {'estado': 'ANULADA', 'total': 2}]
    data_estados = Cita.objects.filter(clinica=mi_clinica).values('estado').annotate(total=Count('id'))
    
    # Preparamos listas para Chart.js
    labels_estado = []
    data_estado_count = []
    for item in data_estados:
        labels_estado.append(item['estado'])
        data_estado_count.append(item['total'])

    # 4. DATOS PARA GRÁFICO 2: Top 5 Tratamientos más vendidos
    top_tratamientos = Cita.objects.filter(clinica=mi_clinica).exclude(estado='ANULADA').values('tratamiento__nombre').annotate(total=Count('id')).order_by('-total')[:5]
    
    labels_top = []
    data_top = []
    for item in top_tratamientos:
        labels_top.append(item['tratamiento__nombre'])
        data_top.append(item['total'])

    context = {
        'ingresos_mes': ingresos_mes,
        'deuda_total': deuda_total,
        # Pasamos las listas directamente. En el template usaremos un filtro 'safe'
        'labels_estado': labels_estado,
        'data_estado_count': data_estado_count,
        'labels_top': labels_top,
        'data_top': data_top,
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def generar_pdf_paciente(request, paciente_id):
    # Importación dentro de la función (como lo dejamos antes)
    import weasyprint
    
    mi_clinica = obtener_clinica_usuario(request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id, clinica=mi_clinica)
    historial = Cita.objects.filter(paciente=paciente, estado='REALIZADA').order_by('-fecha')

    # --- LÓGICA BLINDADA PARA EL LOGO ---
    logo_src = ""
    try:
        if mi_clinica.logo and hasattr(mi_clinica.logo, 'path'):
            # Verificamos si el archivo existe físicamente en el servidor
            if os.path.exists(mi_clinica.logo.path):
                # En Linux (Railway) las rutas ya empiezan con /, así que solo agregamos file://
                # En Windows, esto también funciona si la ruta es absoluta
                logo_src = 'file://' + mi_clinica.logo.path
            else:
                print("⚠ El archivo de imagen no existe en la ruta:", mi_clinica.logo.path)
    except Exception as e:
        print(f"Error cargando imagen (El PDF se generará sin logo): {e}")
        logo_src = ""
    
    # ------------------------------------

    context = {
        'paciente': paciente,
        'historial': historial,
        'clinica': mi_clinica,
        'fecha_hoy': datetime.now(),
        'kinesiologo': request.user.get_full_name() or request.user.username,
        'logo_src': logo_src  # Pasamos la variable segura
    }

    # ... resto del código igual ...
    html_string = render_to_string('core/reporte_pdf.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=Ficha_{paciente.rut}.pdf'
    response.write(result)
    
    return response

@login_required
def editar_paciente(request, paciente_id):
    mi_clinica = obtener_clinica_usuario(request.user)
    # Buscamos al paciente, asegurándonos que sea de MI clínica (seguridad)
    paciente = get_object_or_404(Paciente, id=paciente_id, clinica=mi_clinica)

    if request.method == 'POST':
        # Pasamos 'instance=paciente' para decirle que estamos ACTUALIZANDO, no creando
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('detalle_paciente', paciente_id=paciente.id)
    else:
        # Pre-llenamos el formulario con los datos actuales
        form = PacienteForm(instance=paciente)

    return render(request, 'core/editar_paciente.html', {
        'form': form, 
        'paciente': paciente
    })

from .forms import ClinicaForm # <--- No olvides importar el nuevo form

@login_required
def configuracion_clinica(request):
    mi_clinica = obtener_clinica_usuario(request.user)
    
    if request.method == 'POST':
        # IMPORTANTE: request.FILES es necesario para subir imágenes
        form = ClinicaForm(request.POST, request.FILES, instance=mi_clinica)
        if form.is_valid():
            form.save()
            # Mensaje de éxito (opcional, pero recomendado)
            return redirect('lista_pacientes')
    else:
        form = ClinicaForm(instance=mi_clinica)

    return render(request, 'core/configuracion_clinica.html', {
        'form': form, 
        'clinica': mi_clinica
    })