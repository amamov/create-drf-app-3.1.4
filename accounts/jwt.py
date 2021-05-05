import jwt
from django.conf import settings
from django.utils import timezone
from django.conf import settings


PROJECT_NAME = settings.JWT_AUTH["PROJECT_NAME"]
JWT_SECRET_KEY = settings.JWT_AUTH["JWT_SECRET_KEY"]
JWT_ALGORITHM = settings.JWT_AUTH["JWT_ALGORITHM"]
ACCESS_TOKEN_EXPIRES_MINUTES = int(settings.JWT_AUTH["ACCESS_TOKEN_EXPIRES_MINUTES"])
REFRESH_TOKEN_EXPIRES_HOURS = int(settings.JWT_AUTH["REFRESH_TOKEN_EXPIRES_HOURS"])


def generate_access_token(user):
    aud = [f"urn:{PROJECT_NAME}:user"]
    if user.is_active:
        aud.append(f"urn:{PROJECT_NAME}:active")
    if user.is_admin:
        aud.append(f"urn:{PROJECT_NAME}:admin")
    iat = timezone.now()
    exp = iat + timezone.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    return (
        jwt.encode(
            {
                "iss": PROJECT_NAME,
                "sub": str(user.uuid),
                "iat": iat,
                "exp": exp,
                "type": "access",
                "aud": aud,
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        ),
        exp.timestamp(),
        timezone.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES).seconds,  # Max-Age
    )


def generate_refresh_token(user, request, refresh_obj):
    user_agent = request.META.get("HTTP_USER_AGENT")
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    refresh_obj.device = user_agent
    refresh_obj.ip = ip
    refresh_obj.last_refreshed = timezone.now()
    refresh_obj.user = user
    refresh_obj.save()
    exp = refresh_obj.last_refreshed + timezone.timedelta(
        hours=REFRESH_TOKEN_EXPIRES_HOURS
    )
    return (
        jwt.encode(
            {
                "iss": PROJECT_NAME,
                "sub": str(refresh_obj.uuid),
                "iat": refresh_obj.last_refreshed,
                "exp": exp,
                "type": "refresh",
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        ),
        timezone.timedelta(hours=REFRESH_TOKEN_EXPIRES_HOURS).seconds,  # Max-Age
    )
