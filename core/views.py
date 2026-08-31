from django.shortcuts import render


def index(request):
    """
    Página principal (home) de Malvinas Gym.

    Es la vista de bienvenida que ve cualquier visitante no autenticado:
    presenta el gimnasio, sus ventajas, clases, planes y datos de contacto.
    """
    context = {
        "gimnasio": {
            "nombre": "Malvinas Gym",
            "barrio": "Barrio Piedrabuena",
            "direccion": "Barrio Piedrabuena, Ciudad Autónoma de Buenos Aires",
            "telefono": "11 2560-8817",
            "email": "contacto@malvinasgym.com.ar",
            "instagram": "@malvinasgym",
        },
        "ventajas": [
            {
                "icono": "fa-solid fa-dumbbell",
                "titulo": "Equipamiento moderno",
                "texto": "Máquinas y equipos de última generación, mantenidos y "
                         "renovados constantemente para tu seguridad y rendimiento.",
            },
            {
                "icono": "fa-solid fa-heart-pulse",
                "titulo": "Plan nutricional saludable",
                "texto": "Acompañamos tu entrenamiento con pautas de alimentación "
                         "pensadas junto a profesionales del área.",
            },
            {
                "icono": "fa-solid fa-user-graduate",
                "titulo": "Entrenamiento profesional",
                "texto": "Profesores capacitados que diseñan rutinas adaptadas a "
                         "cada objetivo, desde principiantes hasta avanzados.",
            },
            {
                "icono": "fa-solid fa-bullseye",
                "titulo": "A tu medida",
                "texto": "Cada cuerpo es distinto: adaptamos intensidad, cargas y "
                         "progresión a tus necesidades particulares.",
            },
        ],
        "clases": [
            {"categoria": "Fuerza", "nombre": "Musculación", "img": "class-1"},
            {"categoria": "Cardio", "nombre": "Ciclismo indoor", "img": "class-2"},
            {"categoria": "Fuerza", "nombre": "Kettlebells", "img": "class-3"},
            {"categoria": "Cardio", "nombre": "Funcional", "img": "class-4"},
            {"categoria": "Entrenamiento", "nombre": "Boxeo", "img": "class-5"},
        ],
        "planes": [
            {
                "nombre": "Clase suelta",
                "precio": "3.500",
                "detalle": "POR CLASE",
                "beneficios": [
                    "Acceso a sala de musculación",
                    "Equipamiento sin límite",
                    "Sin permanencia mínima",
                ],
                "destacado": False,
            },
            {
                "nombre": "Mensual full",
                "precio": "18.000",
                "detalle": "POR MES",
                "beneficios": [
                    "Acceso ilimitado todo el mes",
                    "Todas las clases grupales",
                    "Seguimiento de un profesor",
                    "Sin horarios restringidos",
                ],
                "destacado": True,
            },
            {
                "nombre": "Trimestral",
                "precio": "48.000",
                "detalle": "CADA 3 MESES",
                "beneficios": [
                    "Acceso ilimitado",
                    "Plan de entrenamiento personalizado",
                    "Evaluación física mensual",
                ],
                "destacado": False,
            },
        ],
    }
    return render(request, "core/index.html", context)
