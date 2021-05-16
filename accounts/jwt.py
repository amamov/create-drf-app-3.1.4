import jwt
from django.conf import settings
from django.utils import timezone
from django.conf import settings


PROJECT_NAME = settings.JWT_AUTH["PROJECT_NAME"]
JWT_SECRET_KEY = settings.JWT_AUTH["JWT_SECRET_KEY"]
JWT_ALGORITHM = settings.JWT_AUTH["JWT_ALGORITHM"]
ACCESS_TOKEN_EXPIRES_HOURS = int(settings.JWT_AUTH["ACCESS_TOKEN_EXPIRES_HOURS"])


def generate_access_token(user, request, token_obj):
    user_agent = request.META.get("HTTP_USER_AGENT")
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    iat = timezone.now()
    token_obj.device = user_agent
    token_obj.ip = ip
    token_obj.last_refreshed = iat
    token_obj.user = user
    token_obj.save()
    aud = [f"urn:{PROJECT_NAME}:user"]
    if user.is_active:
        aud.append(f"urn:{PROJECT_NAME}:active")
    if user.is_admin:
        aud.append(f"urn:{PROJECT_NAME}:admin")
    exp = iat + timezone.timedelta(hours=ACCESS_TOKEN_EXPIRES_HOURS)
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
    )
