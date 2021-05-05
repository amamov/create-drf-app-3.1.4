import jwt
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

User = get_user_model()

PROJECT_NAME = settings.JWT_AUTH["PROJECT_NAME"]
JWT_SECRET_KEY = settings.JWT_AUTH["JWT_SECRET_KEY"]
JWT_ALGORITHM = settings.JWT_AUTH["JWT_ALGORITHM"]


class JWTAuthentication(authentication.BaseAuthentication):

    """
    [header]
    AUTHORIZATION : Bearer header.payload.Signature
    """

    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        print(token)
        if not token:
            return None
        try:
            token = token.split(" ")
            if token[0] != "Bearer":
                return None
            token = token[1]
            access_data = jwt.decode(
                token,
                JWT_SECRET_KEY,
                JWT_ALGORITHM,
                audience=f"urn:{PROJECT_NAME}:user",
            )
            if access_data["type"] != "access":
                return None
            uuid = access_data["sub"]
            user = User.objects.get(uuid=uuid)
            if user.refresh_tokens.count() == 0:
                msg = _("Invalid authentication access.")
                raise exceptions.AuthenticationFailed(msg)
            return user, None
        except (
            IndexError,
            KeyError,
            jwt.exceptions.DecodeError,
            jwt.ExpiredSignatureError,
            User.DoesNotExist,
            exceptions.AuthenticationFailed,
        ):
            return None
