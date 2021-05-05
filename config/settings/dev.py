from .base import *

DEBUG = True
SESSION_COOKIE_SECURE = False

# django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True

# django-debug-toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
INTERNAL_IPS = ["127.0.0.1"]

# drf-yasg
INSTALLED_APPS += ["drf_yasg"]

# Database
"""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
"""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ["DB_USER"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'",},
    }
}
