from pathlib import Path
import environ
import os
import logging
from datetime import timedelta
import dj_database_url
import cloudinary

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Debug print env vars directly!
print("[DEBUG] ENVIRONMENT VARIABLES:")
print(f"[DEBUG] CLOUD_NAME: {os.environ.get('CLOUD_NAME')}")
print(f"[DEBUG] API_KEY: {os.environ.get('API_KEY')}")
print(
    f"[DEBUG] API_SECRET: {'*' * len(os.environ.get('API_SECRET', '')) if os.environ.get('API_SECRET') else 'None'}"
)

# Logging configuration - FIRST! So we can log everything!
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {  # our settings.py logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "vehicles": {  # our vehicles app logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS", default=["localhost", "127.0.0.1", ".onrender.com"]
)

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://m-motors-ochre.vercel.app",
    ],
)

CORS_ALLOW_CREDENTIALS = True


# Application definition
INSTALLED_APPS = [
    # ----- Cloudinary -----
    "cloudinary_storage",
    "cloudinary",
    # ----- Django Core -----
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ----- REST FRAMEWORK -----
    "rest_framework",
    # ----- CORS HEADERS -----
    "corsheaders",
    # ----- ENVIRON -----
    "environ",
    # ----- DRF SPECTACULAR -----
    "drf_spectacular",
    # ----- APPS -----
    "users",
    "folders",
    "vehicles",
    # ----- STORAGE -----
    "storages",
    # ----- FILTERS -----
    "django_filters",
]

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


# Database
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"), conn_max_age=600, ssl_require=True
    )
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "users.authentication.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# DRF Spectacular Settings
SPECTACULAR_SETTINGS = {
    "TITLE": "M-Motors API",
    "DESCRIPTION": "Cette API REST permet de gérer l'intégralité du nouveau service de location longue durée avec option d'achat (LLD+OA) proposé par l'entreprise. Elle alimente l'application web refondue (frontend Next.js) et le back-office.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {
            "name": "users",
            "description": "Gestion des utilisateurs et authentification",
        },
        {"name": "vehicles", "description": "Gestion du catalogue des véhicules"},
        {"name": "folders", "description": "Dossiers clients"},
    ],
}

# --- Cloudinary configuration for media files ---
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUD_NAME", default=""),
    "API_KEY": env("API_KEY", default=""),
    "API_SECRET": env("API_SECRET", default=""),
}

# Initialize Cloudinary
logger = logging.getLogger(__name__)
cloud_name = CLOUDINARY_STORAGE.get("CLOUD_NAME")
api_key = CLOUDINARY_STORAGE.get("API_KEY")
api_secret = CLOUDINARY_STORAGE.get("API_SECRET")

logger.info(
    f"[DEBUG] Cloudinary config: CLOUD_NAME='{cloud_name}', API_KEY='{api_key}', API_SECRET='{'*'*len(api_secret) if api_secret else ''}'"
)

if cloud_name and api_key and api_secret:
    logger.info("[DEBUG] Using Cloudinary storage!")
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
    )
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    logger.critical("[DEBUG] ⚠️ CLOUDINARY CREDENTIALS MISSING! Using local storage! ⚠️")
    logger.critical(
        f"[DEBUG] CLOUD_NAME: '{cloud_name}', API_KEY: '{api_key}', API_SECRET: '{'*'*len(api_secret) if api_secret else ''}'"
    )
    # Fallback to local storage if Cloudinary not configured
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# base URL for media files
if not cloud_name or not api_key or not api_secret:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Email configuration for development (console backend)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@mmotors.com"
FRONTEND_URL = "http://localhost:3000"
