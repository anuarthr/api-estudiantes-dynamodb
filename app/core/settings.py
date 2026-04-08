import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-key-change-in-production")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "rest_framework",
    "drf_spectacular",
    "estudiantes",
    "notas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "core.urls"

# Requerido por drf-spectacular para renderizar Swagger UI
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

WSGI_APPLICATION = "core.wsgi.application"

# Sin base de datos relacional — usamos DynamoDB directamente con boto3
DATABASES = {}

REST_FRAMEWORK = {
    # Solo JSON, sin la interfaz HTML navegable de DRF
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # API pública — sin autenticación ni permisos
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    # Sin django.contrib.auth — evita que DRF intente cargar AnonymousUser
    "UNAUTHENTICATED_USER": None,
    # Esquema OpenAPI generado automáticamente por drf-spectacular
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API Estudiantes - DynamoDB Local",
    "DESCRIPTION": "API REST para gestión de estudiantes y notas. Proyecto bases de datos no relacionales.",
    "VERSION": "1.0.0",
}
