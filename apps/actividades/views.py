import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ActividadForm, AsistenciaForm, HorarioForm, InscripcionForm
from .models import (
    NOMBRES_ESTADOS_PREDEFINIDOS,
    Actividad,
    Asistencia,
    EstadoActividad,
    Horario,
    Inscripcion,
)


def _eliminar_con_proteccion(request, obj, lista_url, mensaje_en_uso):
    """Borra `obj` y redirige a `lista_url`. Si tiene registros
    relacionados con on_delete=PROTECT, avisa en vez de tirar un error
    500 (mismo criterio que apps.socios.views.eliminar_socio)."""
    nombre = str(obj)

    try:
        obj.delete()
    except ProtectedError:
        messages.error(request, f'No se puede eliminar "{nombre}": {mensaje_en_uso}')
        return redirect(lista_url)

    messages.success(request, f'"{nombre}" fue eliminado correctamente.')
    return redirect(lista_url)


# ---------------------------------------------------------------------
# Actividad
#
# No hay ABM de EstadoActividad: los tres estados (Activo, Inactivo,
# Suspendido) son fijos y se siembran por migración
# (0007_seed_estados_predefinidos). El administrador ya no tiene forma
# de crear o editar estados a mano.
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_actividad", raise_exception=True)
def lista_actividades(request):
    buscar = request.GET.get("buscar", "").strip()
    estado_id = request.GET.get("estado", "").strip()

    actividades = Actividad.objects.select_related("estado_actividad").all()

    if buscar:
        actividades = actividades.filter(Q(nombre__icontains=buscar))

    if estado_id:
        actividades = actividades.filter(estado_actividad_id=estado_id)

    paginator = Paginator(actividades, 10)
    pagina = request.GET.get("page")

    estados_filtro = EstadoActividad.objects.filter(
        nombre__in=NOMBRES_ESTADOS_PREDEFINIDOS
    )

    contexto = {
        "actividades": paginator.get_page(pagina),
        "buscar": buscar,
        "estado_id": estado_id,
        "estados_filtro": estados_filtro,
        "total_actividades": Actividad.objects.count(),
    }

    # El selector de estado y el botón "Limpiar filtros" actualizan la
    # lista sin recargar la página completa (mismo criterio que
    # apps.socios.views.lista_socios): si la petición viene por fetch()
    # con este header, solo se devuelve el fragmento de resultados.
    plantilla = (
        "actividades/_resultados_actividades.html"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest"
        else "actividades/lista_actividades.html"
    )

    return render(request, plantilla, contexto)


@login_required
@permission_required("actividades.view_actividad", raise_exception=True)
def detalle_actividad(request, pk):
    actividad = get_object_or_404(
        Actividad.objects.select_related("estado_actividad"), pk=pk
    )
    horarios = actividad.horarios.select_related("profesor").all()

    return render(
        request,
        "actividades/detalle_actividad.html",
        {"actividad": actividad, "horarios": horarios},
    )


@login_required
@permission_required("actividades.add_actividad", raise_exception=True)
def crear_actividad(request):
    form = ActividadForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        actividad = form.save()
        messages.success(request, f'La actividad "{actividad}" fue creada correctamente.')
        return redirect("actividades:actividad_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Nueva actividad", "cancelar_url": "actividades:actividad_lista"},
    )


@login_required
@permission_required("actividades.change_actividad", raise_exception=True)
def editar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    form = ActividadForm(request.POST or None, instance=actividad)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f'La actividad "{actividad}" fue actualizada correctamente.')
        return redirect("actividades:actividad_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Editar actividad", "cancelar_url": "actividades:actividad_lista"},
    )


@login_required
@permission_required("actividades.delete_actividad", raise_exception=True)
def eliminar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            actividad,
            "actividades:actividad_lista",
            "todavía tiene horarios asociados.",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {"objeto": actividad, "cancelar_url": "actividades:actividad_lista"},
    )


# ---------------------------------------------------------------------
# Horario
#
# Tampoco hay ABM de EstadoProfesor, por la misma razón que
# EstadoActividad de arriba.
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_horario", raise_exception=True)
def lista_horarios(request):
    horarios = Horario.objects.select_related("actividad", "profesor").all()

    paginator = Paginator(horarios, 10)
    pagina = request.GET.get("page")

    return render(
        request,
        "actividades/lista_horarios.html",
        {"horarios": paginator.get_page(pagina)},
    )


@login_required
@permission_required("actividades.view_horario", raise_exception=True)
def detalle_horario(request, pk):
    horario = get_object_or_404(
        Horario.objects.select_related("actividad", "profesor"), pk=pk
    )
    inscriptos = horario.inscripciones.select_related("socio").all()

    return render(
        request,
        "actividades/detalle_horario.html",
        {"horario": horario, "inscriptos": inscriptos},
    )


@login_required
@permission_required("actividades.add_horario", raise_exception=True)
def crear_horario(request):
    form = HorarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        horario = form.save()
        messages.success(request, f'El horario "{horario}" fue creado correctamente.')
        return redirect("actividades:horario_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Nuevo horario", "cancelar_url": "actividades:horario_lista"},
    )


@login_required
@permission_required("actividades.change_horario", raise_exception=True)
def editar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    form = HorarioForm(request.POST or None, instance=horario)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f'El horario "{horario}" fue actualizado correctamente.')
        return redirect("actividades:horario_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Editar horario", "cancelar_url": "actividades:horario_lista"},
    )


@login_required
@permission_required("actividades.delete_horario", raise_exception=True)
def eliminar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            horario,
            "actividades:horario_lista",
            "todavía tiene asistencias registradas (las inscripciones sí "
            "se eliminarían junto con el horario).",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {
            "objeto": horario,
            "cancelar_url": "actividades:horario_lista",
            "advertencia": (
                "Eliminar este horario también eliminará todas las "
                "inscripciones asociadas a él."
            ),
        },
    )


# ---------------------------------------------------------------------
# Inscripcion (sin cambios en esta revisión)
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_inscripcion", raise_exception=True)
def lista_inscripciones(request):
    inscripciones = Inscripcion.objects.select_related(
        "socio", "horario", "horario__actividad"
    ).all()

    paginator = Paginator(inscripciones, 10)
    pagina = request.GET.get("page")

    return render(
        request,
        "actividades/lista_inscripciones.html",
        {"inscripciones": paginator.get_page(pagina)},
    )


@login_required
@permission_required("actividades.add_inscripcion", raise_exception=True)
def crear_inscripcion(request):
    form = InscripcionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        inscripcion = form.save()
        messages.success(request, f'Inscripción registrada: {inscripcion}.')
        return redirect("actividades:inscripcion_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Nueva inscripción", "cancelar_url": "actividades:inscripcion_lista"},
    )


@login_required
@permission_required("actividades.change_inscripcion", raise_exception=True)
def editar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    form = InscripcionForm(request.POST or None, instance=inscripcion)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La inscripción fue actualizada correctamente.")
        return redirect("actividades:inscripcion_lista")

    return render(
        request,
        "actividades/form_generico.html",
        {"form": form, "titulo": "Editar inscripción", "cancelar_url": "actividades:inscripcion_lista"},
    )


@login_required
@permission_required("actividades.delete_inscripcion", raise_exception=True)
def eliminar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            inscripcion,
            "actividades:inscripcion_lista",
            "no se pudo eliminar.",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {"objeto": inscripcion, "cancelar_url": "actividades:inscripcion_lista"},
    )


# ---------------------------------------------------------------------
# Asistencia
#
# Rediseño completo del módulo. Ya no existe un alta libre (elegir
# cualquier socio + cualquier horario + cualquier profesor + fecha/hora
# a mano). La única forma de generar asistencias es "tomar asistencia"
# sobre un horario puntual: se listan los socios ya inscriptos en ese
# horario y se marca presente/ausente. Editar y eliminar un registro
# puntual se mantienen para corregir errores de carga.
# ---------------------------------------------------------------------

@login_required
@permission_required("actividades.view_asistencia", raise_exception=True)
def lista_asistencias(request):
    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "").strip()

    asistencias = Asistencia.objects.select_related(
        "socio", "horario", "horario__actividad", "profesor"
    ).all()

    if buscar:
        asistencias = asistencias.filter(horario__actividad__nombre__icontains=buscar)

    if estado == "presente":
        asistencias = asistencias.filter(presente=True)
    elif estado == "ausente":
        asistencias = asistencias.filter(presente=False)

    paginator = Paginator(asistencias, 15)
    pagina = request.GET.get("page")

    return render(
        request,
        "actividades/lista_asistencias.html",
        {
            "asistencias": paginator.get_page(pagina),
            "buscar": buscar,
            "estado": estado,
        },
    )


@login_required
@permission_required("actividades.view_asistencia", raise_exception=True)
def detalle_asistencia(request, pk):
    asistencia = get_object_or_404(
        Asistencia.objects.select_related("socio", "horario", "horario__actividad", "profesor"),
        pk=pk,
    )

    return render(request, "actividades/detalle_asistencia.html", {"asistencia": asistencia})


@login_required
@permission_required("actividades.add_asistencia", raise_exception=True)
def tomar_asistencia(request, horario_id):
    """Reemplaza al alta libre de asistencias. Muestra la lista cerrada
    de socios inscriptos en `horario` y permite marcar presente/ausente
    para la fecha indicada (hoy por defecto). Todos parten marcados
    Presente; el profesor solo toca los que faltaron."""
    horario = get_object_or_404(
        Horario.objects.select_related("actividad", "profesor"), pk=horario_id
    )

    fecha_str = request.GET.get("fecha") or request.POST.get("fecha")
    try:
        fecha = datetime.date.fromisoformat(fecha_str) if fecha_str else datetime.date.today()
    except ValueError:
        fecha = datetime.date.today()

    inscripciones = horario.inscripciones.select_related("socio").order_by(
        "socio__apellido", "socio__nombre"
    )

    asistencias_existentes = {
        a.socio_id: a
        for a in Asistencia.objects.filter(horario=horario, fecha=fecha)
    }

    if request.method == "POST":
        ahora = datetime.datetime.now().time()

        for inscripcion in inscripciones:
            socio_id = inscripcion.socio_id
            # Cada socio llega marcado "presente" salvo que el profesor
            # haya tocado el botón "Ausente" (name=f"estado_{socio_id}",
            # value="ausente").
            presente = request.POST.get(f"estado_{socio_id}") != "ausente"

            Asistencia.objects.update_or_create(
                socio_id=socio_id,
                horario=horario,
                fecha=fecha,
                defaults={
                    "profesor": horario.profesor,
                    "hora": asistencias_existentes.get(socio_id).hora
                    if socio_id in asistencias_existentes
                    else ahora,
                    "presente": presente,
                },
            )

        messages.success(
            request,
            f"Asistencia de {inscripciones.count()} socios registrada para "
            f'"{horario}" el {fecha.strftime("%d/%m/%Y")}.',
        )
        return redirect("actividades:asistencia_lista")

    filas = [
        {
            "socio": inscripcion.socio,
            "presente": asistencias_existentes.get(inscripcion.socio_id).presente
            if inscripcion.socio_id in asistencias_existentes
            else True,
        }
        for inscripcion in inscripciones
    ]

    return render(
        request,
        "actividades/tomar_asistencia.html",
        {"horario": horario, "fecha": fecha, "filas": filas},
    )


@login_required
@permission_required("actividades.change_asistencia", raise_exception=True)
def editar_asistencia(request, pk):
    asistencia = get_object_or_404(
        Asistencia.objects.select_related("socio", "horario", "profesor"), pk=pk
    )
    form = AsistenciaForm(request.POST or None, instance=asistencia)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La asistencia fue actualizada correctamente.")
        return redirect("actividades:asistencia_lista")

    return render(
        request,
        "actividades/editar_asistencia.html",
        {"form": form, "asistencia": asistencia},
    )


@login_required
@permission_required("actividades.delete_asistencia", raise_exception=True)
def eliminar_asistencia(request, pk):
    asistencia = get_object_or_404(Asistencia, pk=pk)

    if request.method == "POST":
        return _eliminar_con_proteccion(
            request,
            asistencia,
            "actividades:asistencia_lista",
            "no se pudo eliminar.",
        )

    return render(
        request,
        "actividades/confirmar_eliminar_generico.html",
        {"objeto": asistencia, "cancelar_url": "actividades:asistencia_lista"},
    )
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Profesor, EstadoProfesor
from .forms import ProfesorForm
from django.db.models import Q

# NOTA DE SEGURIDAD: estas vistas de Profesor no tenían NINGÚN control de
# autenticación ni de permisos (a diferencia de todo el resto del módulo,
# que usa @login_required + @permission_required en cada vista). Se
# agregan los mixins correspondientes para dejarlas consistentes con el
# resto de la app. Actualmente no están enrutadas en urls.py (código sin
# usar todavía); igual se protegen para que, el día que se las enrute,
# no queden expuestas por descuido.

# 1. LISTAR PROFESORES
class ProfesorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "actividades.view_profesor"
    model = Profesor
    template_name = 'profesores/profesor_list.html'
    context_object_name = 'profesores'

    def get_queryset(self):
        queryset = Profesor.objects.select_related('estado_profesor')

        # BUSCADOR
        buscar = self.request.GET.get('buscar', '').strip()

        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido__icontains=buscar) |
                Q(dni__icontains=buscar)
            )

        # FILTRO POR ESTADO
        estado = self.request.GET.get('estado', '').strip()

        if estado:
            queryset = queryset.filter(
                estado_profesor_id=estado
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # CONTADORES
        queryset_base = Profesor.objects.all()

        context['profesores_totales'] = queryset_base.count()

        context['profesores_activos'] = queryset_base.filter(
            estado_profesor__nombre__iexact='Activo'
        ).count()

        context['profesores_inactivos'] = queryset_base.exclude(
            estado_profesor__nombre__iexact='Activo'
        ).count()

        # VALORES ACTUALES DE LOS FILTROS
        context['buscar'] = self.request.GET.get('buscar', '')
        context['estado_seleccionado'] = self.request.GET.get('estado', '')

        # ESTADOS DEL DESPLEGABLE
        context['estados'] = EstadoProfesor.objects.all().order_by('nombre')

        # CANTIDAD DE RESULTADOS
        context['cantidad_resultados'] = self.get_queryset().count()

        return context

# 2. CREAR PROFESOR
class ProfesorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "actividades.add_profesor"
    model = Profesor
    form_class = ProfesorForm
    template_name = 'profesores/profesor_form.html'
    success_url = reverse_lazy('actividades:profesor_list')

# 3. EDITAR PROFESOR
class ProfesorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "actividades.change_profesor"
    model = Profesor
    form_class = ProfesorForm
    template_name = 'profesores/profesor_form.html'
    success_url = reverse_lazy('actividades:profesor_list')

# 4. ELIMINAR PROFESOR
class ProfesorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "actividades.delete_profesor"
    model = Profesor
    template_name = 'profesores/profesor_confirm_delete.html'
    success_url = reverse_lazy('actividades:profesor_list')

# 5. DETALLE PROFESOR
class ProfesorDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "actividades.view_profesor"
    model = Profesor
    template_name = 'profesores/profesor_detalle.html'
    context_object_name = 'profesor'

# 6. CAMBIAR ESTADO PROFESOR (ACCIÓN RÁPIDA DE ALTA/BAJA)
# Antes era un GET sin login ni permisos: cualquiera (ni siquiera hacía
# falta estar autenticado) podía activar/desactivar profesores con solo
# visitar la URL, y al ser GET quedaba además expuesto a CSRF/prefetch
# (un navegador, proxy o bot que precargue el link ya dispara el cambio).
# Se exige POST + login + permiso, igual que el resto de las acciones que
# modifican estado en el proyecto (ver dar_baja_socio, suspender_socio, etc.)
@login_required
@permission_required("actividades.change_profesor", raise_exception=True)
@require_POST
def cambiar_estado_profesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    
    # Alterna dinámicamente entre Activo e Inactivo
    if profesor.estado_profesor and profesor.estado_profesor.nombre.lower() == 'activo':
        nuevo_estado = EstadoProfesor.objects.get(nombre__iexact='Inactivo')
    else:
        nuevo_estado = EstadoProfesor.objects.get(nombre__iexact='Activo')
        
    profesor.estado_profesor = nuevo_estado
    profesor.save()
    
    # Redirige nuevamente a la misma pantalla de edición para ver el cambio
    return redirect('actividades:profesor_list')