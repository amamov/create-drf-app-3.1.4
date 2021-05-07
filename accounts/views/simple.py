"""
not using refresh token
오직 acess token만 사용
"""

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from accounts.authentication import JWTCookieAuthentication
from accounts.jwt import generate_access_token
from accounts.permissions import IsAuthenticated


PROJECT_NAME = settings.JWT_AUTH["PROJECT_NAME"]
JWT_SECRET_KEY = settings.JWT_AUTH["JWT_SECRET_KEY"]
JWT_ALGORITHM = settings.JWT_AUTH["JWT_ALGORITHM"]


@api_view(["POST"])
@authentication_classes([JWTCookieAuthentication])
def login_view(request):
    """ POST {"email", "password"} """

    email = request.data.get("email")
    password = request.data.get("password")

    if not email and password:
        return Response(
            data={
                "success": False,
                "message": "Field Error",
                "client": "이메일 또는 비밀번호를 확인해주세요.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = authenticate(email=email, password=password)
    if user:
        access_token, _, max_age = generate_access_token(user)

        response = Response(
            data={"success": True, "client": "반갑습니다. :)"}, status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="accessToken", value=access_token, max_age=max_age, httponly=True,
        )

        return response
    else:
        return Response(
            data={
                "success": False,
                "message": "Authentication Error",
                "client": "이메일 또는 비밀번호를 확인해주세요.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["DELETE"])
@authentication_classes([JWTCookieAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    response = Response(data={"success": True,}, status=status.HTTP_200_OK,)
    response.delete_cookie("accessToken")
    return response
