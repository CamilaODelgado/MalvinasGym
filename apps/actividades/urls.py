from django.urls import path

from . import views 

from .views import (
    ProfesorListView,
    ProfesorCreateView,
    ProfesorUpdateView,
    ProfesorDeleteView,
    ProfesorDetailView,
    cambiar_estado_profesor
)


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
    
    # Profesores
    # NOTA: antes esta ruta era path('', ...) — literalmente la misma
    # regex vacía que "actividad_lista" más arriba. Django resuelve por
    # orden de aparición, así que /actividades/ siempre caía en
    # lista_actividades y esta vista quedaba inalcanzable por URL (aunque
    # el name="profesor_list" existía y {% url %} lo resolvía "bien",
    # apuntando sin querer a esa misma URL compartida). Se le da su propio
    # prefijo, en línea con el resto de las rutas de profesores de abajo.
    path('profesores/', ProfesorListView.as_view(), name='profesor_list'),
    path('profesores/crear/', ProfesorCreateView.as_view(), name='profesor_create'),
    path('profesores/<int:pk>/editar/', ProfesorUpdateView.as_view(), name='profesor_update'),
    path('profesores/<int:pk>/eliminar/', ProfesorDeleteView.as_view(), name='profesor_delete'),
    path('profesores/<int:pk>/detalle/', ProfesorDetailView.as_view(), name='profesor_detalle'),
    path('profesores/<int:pk>/cambiar-estado/', cambiar_estado_profesor, name='profesor_cambiar_estado'),
    
]
