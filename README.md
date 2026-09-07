# Malvinas GYM — Backend Django

Sistema de gestión y facturación para un gimnasio de Barrio Piedrabuena,
Ciudad Autónoma de Buenos Aires. Desarrollado por el equipo estudiantil
**Ascent Solutions**, bajo la supervisión del profesor Héctor Fernández.

## Arquitectura

El proyecto sigue una arquitectura de **apps por dominio**, correcta para
este tamaño de sistema:

| App               | Responsabilidad                                          |
|-------------------|-----------------------------------------------------------|
| `core`            | Landing pública y configuración general del gimnasio      |
| `usuarios`        | Usuario custom (`AUTH_USER_MODEL`), roles y estados        |
| `socios`          | Socios, responsables (para menores), apto físico y su CRUD de gestión |
| `actividades`     | Profesores, actividades, horarios, inscripciones, asistencia |
| `membresias`      | Planes y membresías de los socios                          |
| `cuotas`          | Facturación periódica de cada membresía                    |
| `caja`            | Apertura/cierre de caja, gastos y movimientos              |
| `notificaciones`  | Notificaciones a socios (email, etc.)                      |
| `dashboard`       | Reservada para reportes/KPIs (todavía sin modelos propios) |

`config/` contiene la configuración del proyecto (settings, urls, wsgi/asgi).

Los modelos de "catálogo" (`Estado*`, `Tipo*`, etc.) son tablas propias en
vez de `choices=` fijos, lo que permite dar de alta nuevos estados/tipos
desde el admin sin migrar. Buena decisión, consistente en todas las apps.

La app `socios` ya tiene un CRUD de gestión completo (listado con
búsqueda/paginación, alta, detalle, edición y baja), con su propio layout
(`base_gestion.html`, sidebar con navegación por módulos). Es el primer
módulo de gestión "real" del proyecto — el resto de las apps todavía solo
tienen modelos y admin.

## Puesta en marcha

```bash
python -m venv venv
source venv/bin/activate        # o venv\Scripts\activate en Windows
pip install -r requirements.txt

copy .env.example .env 
o
cp .env.example .env            # completar credenciales de Postgres
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Si no se define `DB_NAME` en el `.env`, el proyecto cae automáticamente a
SQLite (pensado solo para levantar rápido en desarrollo sin instalar
Postgres localmente). Para un entorno real, completar las variables
`DB_*` del `.env.example`.

La migración `core.0002_seed_configuracion_gimnasio` carga automáticamente
una fila inicial de `ConfiguracionGimnasio` para que la home tenga datos
reales desde el primer `migrate`.

Para entrar al panel de gestión (`/socios/`), hace falta iniciar sesión
en `/accounts/login/` con un usuario que tenga los permisos de socios
(`view_socio`, `add_socio`, `change_socio`, `delete_socio` — un
superusuario los tiene todos).

## Cambios realizados

Esta es la segunda pasada de revisión sobre el proyecto. Desde la
anterior, el equipo migró la base a Postgres y construyó el primer CRUD
real (gestión de socios: modelos, formulario, vistas y templates). Ese
avance es bueno, pero trajo problemas nuevos además de que varios de los
puntos de la revisión de configuración anterior no se habían aplicado
todavía sobre esta rama. Se corrigió lo siguiente:

### 🔴 Seguridad: el CRUD de socios era completamente público

`apps/socios/views.py` importaba `login_required` y `permission_required`
pero **no los aplicaba a ninguna vista**. Cualquiera que conociera la URL
`/socios/` podía ver el listado completo de socios (DNI, teléfono,
domicilio, contacto de emergencia, estado del apto físico) sin iniciar
sesión, y también podía crear, editar o eliminar socios sin ningún
control. El propio template (`base_gestion.html`) ya asumía que esto
estaba protegido — usa `{% if perms.socios.view_socio %}` para mostrar el
link del menú — pero la vista detrás no lo verificaba. Se agregaron los
decoradores correspondientes a las cinco vistas (`view_socio` para
listar/ver, `add_socio`, `change_socio`, `delete_socio`), y se configuró
`django.contrib.auth.urls` + un template de login mínimo para que el
`login_required` tenga a dónde mandar a alguien no autenticado.

### 🔴 Bug: tres de las cinco páginas de socios daban error

Los templates existían con nombres en **plural**
(`form_socios.html`, `detalle_socios.html`,
`confirmar_eliminar_socios.html`) pero las vistas pedían renderizar
nombres en **singular** (`form_socio.html`, `detalle_socio.html`,
`confirmar_eliminar.html`). Además, los tres archivos estaban
completamente vacíos. En la práctica, esto significaba que crear, editar,
ver el detalle o eliminar un socio tiraba `TemplateDoesNotExist` — solo el
listado funcionaba. Se renombraron los archivos para que coincidan con lo
que piden las vistas y se escribió el contenido real de las tres
pantallas, siguiendo el mismo estilo visual que ya tenía `lista_socios.html`.

### 🔴 Bug: eliminar un socio con membresías rompía con error 500

`Membresia.socio`, `Cuota` (vía membresía), `Inscripcion` y `Asistencia`
usan `on_delete=PROTECT` hacia `Socio` a propósito, para no perder
historial de facturación. Pero `eliminar_socio` hacía `socio.delete()`
sin capturar `ProtectedError`, así que intentar borrar cualquier socio con
membresía activa mostraba una página de error de Django en vez de un
aviso entendible. Se capturó la excepción y ahora se muestra un mensaje
claro sugiriendo dar de baja al socio (cambiar su estado) en vez de
eliminarlo.

### 🟡 Bug: los mensajes de éxito/error nunca se mostraban

Las vistas ya usaban `django.contrib.messages` (`messages.success(...)`,
`messages.error(...)`) correctamente, pero **ningún template los
renderizaba** — ni `base.html` ni `base_gestion.html` tenían el bloque
`{% if messages %}`. Esto significa que, por ejemplo, al eliminar
exitosamente un socio, o al toparse con el error de arriba, la persona
usuaria no veía ningún aviso: la página simplemente cambiaba sin
explicación. Se agregó el bloque de mensajes a `base_gestion.html` (con
sus estilos) y se verificó que ahora se muestran.

### 🟡 Código duplicado en `lista_socios`

El bloque que aplica el filtro de búsqueda (`Q(dni__icontains=...) | ...`)
estaba copiado y pegado dos veces seguidas — hacía exactamente lo mismo
las dos veces, sin ningún efecto adicional aparte de ejecutar el mismo
filtro sobre el queryset ya filtrado. Se dejó una sola vez.

### Configuración (`config/settings.py`)

Los mismos problemas de la revisión anterior seguían presentes en esta
rama (el fix previo no se había traído acá):

- `SECRET_KEY`/`DEBUG` hardcodeados pese a tener `python-dotenv`
  importado; `load_dotenv()` duplicado. Ahora se leen del entorno
  (ver `.env.example`).
- `MAILERS` no es un setting real de Django (`EMAIL_BACKEND` es el
  correcto) — no tenía ningún efecto. Corregido.
- `LANGUAGE_CODE`/`TIME_ZONE` en inglés/UTC para un gimnasio en CABA.
  Cambiados a `es-ar` / `America/Argentina/Buenos_Aires`.
- Faltaban `MEDIA_URL`/`MEDIA_ROOT`, necesarios para que
  `Socio.apto_fisico` (un `FileField`) tenga dónde guardar los archivos.
  Se agregaron, y `config/urls.py` ahora sirve `MEDIA_URL` en `DEBUG`.
- Se agregó `STATIC_ROOT` y `DEFAULT_AUTO_FIELD` explícito.
- **Nuevo en esta rama:** la conexión a Postgres estaba bien planteada
  (credenciales desde variables `DB_*`), pero exigía tener Postgres
  corriendo incluso para un `check` o `makemigrations` rápido en
  desarrollo. Se agregó un *fallback* a SQLite cuando `DB_NAME` no está
  definido, para poder levantar el proyecto sin instalar Postgres
  localmente; con `DB_NAME` definido, sigue usando Postgres normalmente.
- Se agregó `LOGIN_URL`/`LOGIN_REDIRECT_URL`/`LOGOUT_REDIRECT_URL`, que
  no existían y ahora hacen falta por los `@login_required` agregados.

### Duplicación de assets estáticos

Existía una carpeta `static/` en la raíz con tres archivos: `favicon.ico`
y `style.css` (copias exactas de los que ya vivían en
`apps/core/static/core/`) y `gestion.css` (el CSS del panel de gestión,
que **solo** existía ahí). Esto era inconsistente: parte de los estilos
del proyecto vivían en la carpeta de la app `core` y parte en una carpeta
suelta en la raíz, sostenida únicamente por `STATICFILES_DIRS`. Se
consolidó todo bajo `apps/core/static/core/` (la convención que ya usa el
resto del proyecto vía `AppDirectoriesFinder`), se eliminó la carpeta
`static/` de la raíz y ya no hace falta declarar `STATICFILES_DIRS`.

### `.gitignore` ignoraba imágenes del sitio

Se había agregado `*.png`, `*.jpg`, `*.jpeg`, `*.webp` al final del
`.gitignore`, seguramente con la intención de ignorar archivos subidos a
`media/`. El problema es que esas reglas son globales: también ignoran
el logo, el favicon, las fotos de clases y la galería que están bajo
`apps/core/static/` y que **sí** deben versionarse — son parte del sitio,
no contenido subido por usuarios. Con este `.gitignore`, cualquiera que
clonara el repo de cero se encontraría con un sitio sin imágenes. Se
quitaron esas reglas; `media/` (donde van los archivos subidos, como el
apto físico) ya estaba cubierto por su propia entrada.

### App `gimnasio` sin uso

La carpeta `apps/gimnasio` seguía existiendo — vacía, y ni siquiera
registrada en `INSTALLED_APPS` esta vez. Es peor que "dead code
registrado": es una carpeta que ni Django carga. Se eliminó.

### Duplicación de datos en la vista principal

Igual que en la revisión anterior: `apps/core/views.index` tenía los
datos de contacto hardcodeados en Python en vez de leer
`ConfiguracionGimnasio` (que existe pero nunca se consultaba). Se corrigió
la vista para leer `ConfiguracionGimnasio.objects.first()`, con un valor
de respaldo solo para una base recién creada, y se agregó la migración de
datos que siembra el registro inicial.

### Validaciones de negocio faltantes

Se reincorporaron las mismas validaciones de la revisión anterior, que no
estaban en esta rama:

- `Horario.clean()`: `hora_fin` debe ser posterior a `hora_inicio`.
- `Cuota.clean()`: el vencimiento no puede ser anterior al período.
- `Caja.clean()`: el cierre no puede ser anterior a la apertura.
- `Socio.clean()`: el apto físico no puede marcarse "Presentado" sin
  archivo ni fecha de presentación.
- `Movimiento`: un movimiento es una cuota **o** un gasto, nunca ambos ni
  ninguno de los dos a la vez sin sentido — `clean()` a nivel de
  formulario/admin y `CheckConstraint` a nivel de base de datos.

### Prolijidad de modelos y admin

Se agregó `Meta` (`verbose_name`, `verbose_name_plural`, `ordering`) a
los ~28 modelos de todas las apps, y se extendió `admin.py` con
`list_display`/`list_filter`/`search_fields` en las apps que solo tenían
`admin.site.register(Modelo)` sin configurar nada (todas menos
`usuarios`, que ya seguía buenas prácticas). También se agregó un inline
de `SocioResponsable` dentro de `Socio`.

## Nuevo módulo: gestión de Actividades

Se construyó el ABM completo (alta, baja, modificación y listado) para
seis modelos de `apps.actividades`, siguiendo el mismo patrón ya
establecido en `apps.socios` (login + permisos por acción, mensajes de
confirmación/error, manejo de `ProtectedError` al eliminar):

- **EstadoActividad** y **EstadoProfesor** — catálogos, con un listado
  genérico compartido (`lista_catalogo.html`).
- **Actividad** — listado con búsqueda por nombre y paginación.
- **Horario** — depende de `Actividad` y `Profesor` (este último se
  sigue gestionando por admin, no forma parte de este entregable).
- **Inscripcion** — depende de `Socio` (ya tiene su propio ABM) y
  `Horario`. El formulario valida que el horario no haya alcanzado su
  cupo antes de guardar; el modelo ya evitaba una inscripción duplicada
  del mismo socio al mismo horario.
- **Asistencia** — depende de `Socio`, `Horario` y `Profesor`.

Todas las vistas de alta/edición reutilizan un único template genérico
(`form_generico.html`), y todas las confirmaciones de baja reutilizan
otro (`confirmar_eliminar_generico.html`) — igual que en `socios`, evita
duplicar el mismo formulario HTML seis veces. Los listados sí tienen su
propio template cada uno, porque cada uno muestra columnas distintas.

Se conectaron los links del sidebar de `base_gestion.html` para
Actividades, Horarios y Asistencias (antes apuntaban a `#`), y se agregó
un ítem nuevo de Inscripciones que no existía. Los catálogos de estados
no tienen entrada propia en el sidebar — se accede a ellos con un botón
"Estados" desde el encabezado del listado de Actividades y de Horarios,
para no saturar el menú principal con dos ítems de uso ocasional.

Se probó el flujo completo de punta a punta (crear estado → actividad →
horario → inscripción → asistencia), incluyendo el rechazo de una
inscripción que supera el cupo del horario y el aviso al intentar
eliminar un horario con asistencias registradas.

## Rediseño: Estados fijos, día controlado y toma de asistencia por lista

A partir de una revisión de UX/lógica de negocio, se corrigieron tres
problemas concretos del módulo de Actividades:

### Los estados dejaron de ser editables a mano

Existían pantallas para que el administrador diera de alta sus propios
"estados de actividad" y "estados de profesor" — lo que permitía cargar
valores arbitrarios o mal escritos (duplicados como "Activo" y "activo",
estados que no significan nada, etc.), visibles después en toda la
interfaz. Se eliminaron esas pantallas por completo (vistas, URLs y
templates): `EstadoActividad` y `EstadoProfesor` siguen existiendo como
tablas (para no romper las relaciones), pero ahora se siembran una única
vez, por migración (`0007_seed_estados_predefinidos`), con los tres
valores fijos del sistema: **Activo, Inactivo, Suspendido**. El
formulario de alta/edición de `Actividad` ya no muestra un desplegable
con todos los estados de la tabla: muestra los tres como botones de
selección rápida (`RadioSelect`), y el formulario no deja elegir ningún
otro valor. La gestión de estos catálogos por Django admin (`/admin/`,
uso técnico/de desarrollo) se mantuvo intacta a propósito — es una
herramienta distinta del panel de gestión que usa el "administrador" del
gimnasio, y sigue siendo útil como vía de escape para un caso excepcional.

### El campo "Día" de un horario ya no acepta texto libre

`Horario.dia` era un `CharField` sin restricciones: se podía escribir
"miercoles" sin tilde, con mayúscula de más, con espacios, etc., y esas
variantes no se reconocían como el mismo día en ningún filtro o reporte.
Se le agregaron `choices` fijos (Lunes a Domingo) tanto al modelo como al
formulario — ahora es un desplegable controlado, no texto libre.

### Asistencias: se eliminó el alta libre y se reemplazó por listas de inscriptos

Este era el problema más serio del sistema: la pantalla de alta permitía
combinar cualquier socio, cualquier horario, cualquier profesor, cualquier
fecha y cualquier hora — sin ninguna relación entre ellos. Se podía
registrar a un socio que ni siquiera estaba inscripto en esa clase, con
un profesor que no la dicta, a las 3 AM. Se eliminó esa pantalla por
completo (`crear_asistencia` y su URL/template ya no existen) y se
reemplazó por un flujo nuevo:

- Desde el listado de **Horarios**, cada fila tiene un botón "Tomar
  asistencia" que lleva a `actividades/horarios/<id>/tomar-asistencia/`.
- Esa pantalla muestra una **lista cerrada**: solo los socios que ya
  están inscriptos (`Inscripcion`) en ese horario específico. No hay
  forma de agregar a alguien que no esté inscripto desde ahí.
- El profesor y el horario ya no se eligen: se toman automáticamente del
  horario sobre el que se está tomando asistencia.
- Cada socio aparece con dos botones — **Presente** / **Ausente** — sin
  ningún desplegable, y **todos parten marcados Presente**. El profesor
  solo tiene que tocar el botón de los pocos que faltaron.
- Al guardar, se crea o actualiza (según la fecha) un registro de
  `Asistencia` por cada socio inscripto, con un nuevo campo booleano
  `presente` (antes no existía forma de registrar una ausencia explícita
  — solo se guardaban las presencias). Es idempotente: si se vuelve a
  tomar asistencia para la misma fecha, actualiza los registros en vez
  de duplicarlos (aprovecha la `UniqueConstraint` que ya tenía el
  modelo sobre socio+horario+fecha).
- Editar y eliminar un registro puntual se mantienen (por si hay que
  corregir un error de carga), pero el formulario de edición
  deliberadamente **no permite reasignar** socio, horario ni profesor —
  solo corregir si estuvo presente/ausente, la fecha o la hora. Permitir
  reasignar esos tres campos habría reabierto el mismo problema que se
  acaba de cerrar.

### Filtros y acciones agregadas

- **Actividades**: filtro rápido por estado (Todas / Activas / Inactivas
  / Suspendidas) junto al buscador, y botón "Ver" en cada fila con el
  detalle de la actividad y sus horarios.
- **Horarios**: botón "Ver" con el detalle del horario y sus inscriptos.
- **Asistencias**: buscador por nombre de actividad (ej. buscar solo
  "Zumba"), filtro rápido Presentes/Ausentes, y botón "Ver" por registro.

## Recomendaciones para seguir mejorando (no aplicadas en esta revisión)

- Escribir tests — para el CRUD de socios, el de actividades, y en
  particular para el flujo de `tomar_asistencia` (creación vs.
  actualización idempotente, marcar ausente, cambiar de fecha).
- Crear grupos de permisos (ej. "Recepción", "Administración") en vez de
  depender de superusuarios para poder usar el panel de gestión.
- Construir el ABM de `Profesor` (hoy solo se gestiona por admin) y
  replicar el patrón de `socios`/`actividades` en el resto de las apps:
  membresías, cuotas, caja.
- Agregar `clean()` a `Membresia`/`Cuota` para impedir superposición de
  membresías activas para el mismo socio, y a `Horario` para impedir que
  un mismo profesor tenga dos horarios superpuestos.
- Extender `Plan` con campos de marketing (`beneficios`, `destacado`) si
  se quiere que la sección de precios de la home se edite desde el admin.
- Endurecer settings de seguridad para producción
  (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`).
