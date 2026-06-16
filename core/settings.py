from pathlib import Path
import os
import environ
import dj_database_url
import cloudinary
import logging
from datetime import timedelta

# ---------------- BASE ----------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ---------------- DEBUG ENV ----------------
print("[DEBUG] ENV LOADED")
print(f"[DEBUG] CLOUD_NAME: {os.environ.get('CLOUD_NAME')}")

# ---------------- SECURITY ----------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS", default=["localhost", "127.0.0.1", ".onrender.com"]
)

# ---------------- APPS ----------------
INSTALLED_APPS = [
    # Cloudinary
    "cloudinary",
    "cloudinary_storage",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    # Storage
    "storages",
    # Apps
    "users",
    "folders",
    "vehicles",
]

# ---------------- MIDDLEWARE ----------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# ---------------- TEMPLATES ----------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ---------------- DATABASE ----------------
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"), conn_max_age=600, ssl_require=True
    )
}

# ---------------- AUTH ----------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------- I18N ----------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# ---------------- STATIC ----------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# IMPORTANT: Django 4+ uses STORAGES ONLY
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---------------- MEDIA ----------------
MEDIA_URL = "/media/"

# ---------------- CLOUDINARY ----------------
cloudinary.config(
    cloud_name=env("CLOUD_NAME", default=""),
    api_key=env("API_KEY", default=""),
    api_secret=env("API_SECRET", default=""),
    secure=True,
)

# ---------------- REST ----------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "users.authentication.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# ---------------- CORS ----------------
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://m-motors-ochre.vercel.app",
    ],
)

CORS_ALLOW_CREDENTIALS = True

# ---------------- LOGGING ----------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# ---------------- DRF SPECTACULAR ----------------
SPECTACULAR_SETTINGS = {
    "TITLE": "M-Motors API",
    "DESCRIPTION": "API LLD+OA pour gestion véhicules",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------- EMAIL ----------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@mmotors.com"
FRONTEND_URL = "http://localhost:3000"
