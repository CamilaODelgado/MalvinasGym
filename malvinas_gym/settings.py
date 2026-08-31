"""
Configuración de Django para el proyecto MalvinasGym.

Generado inicialmente con 'django-admin startproject' y personalizado
para el sitio de Malvinas Gym (Barrio Piedrabuena).
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# SEGURIDAD
# ------------------------------------------------------------------
# ADVERTENCIA: en producción, mové esta clave a una variable de entorno
# y nunca la subas a un repositorio público.
SECRET_KEY = 'django-insecure-wyq0rwalmq43-_bkcs(wv_ytirm&$2zk6qz+lm^bs*rher)5y$'

# ADVERTENCIA: DEBUG debe estar en False en producción.
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ------------------------------------------------------------------
# APLICACIONES INSTALADAS
# ------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps propias
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'malvinas_gym.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Carpeta global de templates (además de la carpeta templates/ de cada app)
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'malvinas_gym.wsgi.application'


# ------------------------------------------------------------------
# BASE DE DATOS
# ------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ------------------------------------------------------------------
# VALIDACIÓN DE CONTRASEÑAS
# ------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ------------------------------------------------------------------
# INTERNACIONALIZACIÓN
# ------------------------------------------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS (CSS, JavaScript, imágenes)
# ------------------------------------------------------------------
STATIC_URL = '/static/'

# Django detecta automáticamente la carpeta core/static/ de la app
# gracias al finder AppDirectoriesFinder (activado por defecto).

# Carpeta donde `collectstatic` reúne todo para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ------------------------------------------------------------------
# CLAVE PRIMARIA POR DEFECTO
# ------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
