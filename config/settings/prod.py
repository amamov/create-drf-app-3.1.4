from .base import *


DEBUG = False
SESSION_COOKIE_SECURE = True

CORS_ORIGIN_ALLOW_ALL = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")

# Storage
INSTALLED_APPS += ["storages"]
STATICFILES_STORAGE = "config.storages.S3StaticStorage"
DEFAULT_FILE_STORAGE = "config.storages.S3MediaStorage"
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_S3_REGION_NAME = os.environ["AWS_S3_REGION_NAME"]  # "ap-northeast-2" 버킷 리전
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]  # 버킷이름
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"  # 버킷에 대한 URL 도메인
)
AWS_DEFAULT_ACL = os.environ["AWS_DEFAULT_ACL"]  # "public-read" 버켓에 대한 엑세스 권한

# DB
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


# DRF
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]

# Log
LOGGING = {
    "version": 1,
    "disable_exiting_loggers": False,
    "handlers": {"console": {"level": "ERROR", "class": "logging.StreamHandler",},},
    "loggers": {"django": {"handlers": ["console"], "level": "ERROR",},},
}
