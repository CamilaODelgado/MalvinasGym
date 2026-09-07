from django.urls import path

from . import views

app_name = "actividades"

urlpatterns = [
    # Actividades
    path("", views.lista_actividades, name="actividad_lista"),
    path("nueva/", views.crear_actividad, name="actividad_crear"),
    path("<int:pk>/", views.detalle_actividad, name="actividad_detalle"),
    path("<int:pk>/editar/", views.editar_actividad, name="actividad_editar"),
    path("<int:pk>/eliminar/", views.eliminar_actividad, name="actividad_eliminar"),

    # Horarios
    path("horarios/", views.lista_horarios, name="horario_lista"),
    path("horarios/nuevo/", views.crear_horario, name="horario_crear"),
    path("horarios/<int:pk>/", views.detalle_horario, name="horario_detalle"),
    path("horarios/<int:pk>/editar/", views.editar_horario, name="horario_editar"),
    path("horarios/<int:pk>/eliminar/", views.eliminar_horario, name="horario_eliminar"),
    path("horarios/<int:horario_id>/tomar-asistencia/", views.tomar_asistencia, name="tomar_asistencia"),

    # Inscripciones
    path("inscripciones/", views.lista_inscripciones, name="inscripcion_lista"),
    path("inscripciones/nueva/", views.crear_inscripcion, name="inscripcion_crear"),
    path("inscripciones/<int:pk>/editar/", views.editar_inscripcion, name="inscripcion_editar"),
    path("inscripciones/<int:pk>/eliminar/", views.eliminar_inscripcion, name="inscripcion_eliminar"),

    # Asistencias
    path("asistencias/", views.lista_asistencias, name="asistencia_lista"),
    path("asistencias/<int:pk>/", views.detalle_asistencia, name="asistencia_detalle"),
    path("asistencias/<int:pk>/editar/", views.editar_asistencia, name="asistencia_editar"),
    path("asistencias/<int:pk>/eliminar/", views.eliminar_asistencia, name="asistencia_eliminar"),
    
]
