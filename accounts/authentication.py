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
    [Header]
    AUTHORIZATION : Bearer header.payload.Signature
    """

    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
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


class JWTCookieAuthentication(authentication.BaseAuthentication):

    """
    [Cookie]
    accessToken=laskdjasljda.djskfhjkd.asldjlaskd
    """

    @classmethod
    def token_parser(cls, cookies: str) -> str:
        cookies: list = cookies.split("; ")
        token = ""
        for cookie in cookies:
            if cookie[:12] == "accessToken=":
                token = cookie[12:]
        return token

    def authenticate(self, request):
        token = request.META.get("HTTP_COOKIE")
        if token is None:
            return None
        token = JWTCookieAuthentication.token_parser(token)
        if token == "":
            return None
        try:
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
        except:
            return None
