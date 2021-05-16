"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.1.2.
"""
import os
from datetime import timedelta
from pathlib import Path

# Build paths insi
# de the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = []

CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = None

# Application definition

INSTALLED_APPS = [
    # Project apps
    "accounts",
    "core",
    # Third party apps
    "admin_interface",  # admin
    "colorfield",  # admin
    "rest_framework",
    "corsheaders",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

X_FRAME_OPTIONS = "SAMEORIGIN"  # admin

MIDDLEWARE = [
    # Third party middleware
    "corsheaders.middleware.CorsMiddleware",
    # Django middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "config" / "templates"),],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "config" / "static",
]
STATIC_ROOT = BASE_DIR / "config" / "staticfiles"  # collectstatic (server root)

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "config" / "media"


# Costum User
AUTH_USER_MODEL = "accounts.User"

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # "accounts.authentication.JWTAuthentication",
        # "accounts.authentication.JWTCookieAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["accounts.permissions.AllowAny",]
    # "DEFAULT_THROTTLE_CLASSES": [
    #     "rest_framework.throttling.AnonRateThrottle",
    #     "rest_framework.throttling.UserRateThrottle",
    # ],
    # "DEFAULT_THROTTLE_RATES": {"anon": "500/day", "user": "500/day"},
}

"""
# Email Configurations
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.mailgun.org")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM")
"""

# JWT
JWT_AUTH = {
    "PROJECT_NAME": os.environ.get("PROJECT_NAME", "amamov"),
    "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY", SECRET_KEY),
    "JWT_ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRES_MINUTES": os.environ.get(
        "JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "2"
    ),
    "REFRESH_TOKEN_EXPIRES_HOURS": os.environ.get("REFRESH_TOKEN_EXPIRES_HOURS", "1"),
}
