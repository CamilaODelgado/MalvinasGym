from django.contrib import admin

from .models import (
    Actividad,
    Asistencia,
    EstadoActividad,
    EstadoProfesor,
    Horario,
    Inscripcion,
    Profesor,
)


@admin.register(EstadoProfesor, EstadoActividad)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "dni", "telefono", "estado_profesor")
    list_filter = ("estado_profesor",)
    search_fields = ("nombre", "apellido", "dni")


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado_actividad", "fecha_creacion")
    list_filter = ("estado_actividad",)
    search_fields = ("nombre",)


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("actividad", "profesor", "dia", "hora_inicio", "hora_fin", "cupo")
    list_filter = ("dia", "actividad")
    search_fields = ("actividad__nombre", "profesor__apellido")


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("socio", "horario", "fecha_inscripcion")
    search_fields = ("socio__nombre", "socio__apellido")


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("socio", "horario", "profesor", "fecha", "hora")
    list_filter = ("fecha",)
    search_fields = ("socio__nombre", "socio__apellido")
