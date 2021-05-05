"""
auth api using httponly cookies. (refreshToken)
rt는 httponly cookie에 저장하고 at는 클라이언트의 로컬 변수에 저장한다.
보안상 안전하지만, 프런트에서 at를 매번 refreshtoken으로 발급받아야 하므로 서버에 부하가 걸리기 쉬울 듯 하다.
"""

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.jwt import generate_access_token, generate_refresh_token
from accounts.permissions import IsAuthenticated
from accounts.models import RefreshToken


PROJECT_NAME = settings.JWT_AUTH["PROJECT_NAME"]
JWT_SECRET_KEY = settings.JWT_AUTH["JWT_SECRET_KEY"]
JWT_ALGORITHM = settings.JWT_AUTH["JWT_ALGORITHM"]


@api_view(["POST"])
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
        access_token, exp_timestamp, _ = generate_access_token(user)
        refresh_obj = RefreshToken()
        refresh_token, max_age = generate_refresh_token(user, request, refresh_obj)
        response = Response(
            data={
                "success": True,
                "accessToken": access_token,
                "accessTokenExp": exp_timestamp,
                "user": {"email": email},
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="refreshToken", value=refresh_token, max_age=max_age, httponly=True,
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


@api_view(["POST"])
def refresh_view(request):
    """ POST """

    refresh_token = request.COOKIES.get("refreshToken", None)  # refresh token 가져오기

    if not refresh_token:
        return Response(
            data={
                "success": False,
                "message": "The token value was not delivered normally.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        decoded_refresh_tk = jwt.decode(
            refresh_token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM
        )
    except jwt.exceptions.DecodeError:
        return Response(
            data={
                "success": False,
                "message": "No valid authentication information was found.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
    try:
        refresh_obj = RefreshToken.objects.get(uuid=decoded_refresh_tk["sub"])
    except RefreshToken.DoesNotExist:
        return Response(
            data={
                "success": False,
                "message": "No valid authentication information was found. Does Not Exist this Refresh Token",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if int(refresh_obj.last_refreshed.timestamp()) != decoded_refresh_tk["iat"]:
        return Response(
            data={
                "success": False,
                "message": "The token issuance times do not match. The token may have been stolen by a malicious user.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh_token, max_age = generate_refresh_token(
        refresh_obj.user, request, refresh_obj
    )
    access_token, exp_timestamp, _ = generate_access_token(refresh_obj.user)

    response = Response(
        data={
            "success": True,
            "message": "Refresh Success",
            "accessToken": access_token,
            "user": {"email": refresh_obj.user.email},
            "accessTokenExp": exp_timestamp,
        },
        status=status.HTTP_200_OK,
    )
    response.set_cookie(
        key="refreshToken", value=refresh_token, max_age=max_age, httponly=True,
    )

    return response


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def all_logout_view(request):
    # 강제 로그아웃 즉, 모든 refresh token을 비운다.
    user = request.user
    user.refresh_tokens.all().delete()
    response = Response(
        data={
            "success": True,
            "message": "All refresh tokens have been removed, and the user's uuid value has been changed.",
        }
    )
    response.delete_cookie("refreshToken")
    return response


@api_view(["POST"])
def logout_view(request):
    """ POST { "refreshToken" } """
    refresh_token = request.COOKIES.get("refreshToken", None)  # refresh token 가져오기

    if not refresh_token:
        return Response(
            data={
                "success": False,
                "message": "The token value was not delivered normally.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        decoded_refresh_tk = jwt.decode(
            refresh_token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM
        )

    except jwt.exceptions.DecodeError:
        # 변조 가증성
        return Response(
            data={
                "success": False,
                "message": "The authentication information is invalid or has expired.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not RefreshToken.objects.filter(uuid=decoded_refresh_tk["sub"]).exists:
        # 변조 가능성
        return Response(
            data={
                "success": False,
                "message": "No valid authentication information was found. You are already logged out.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
    try:
        # 로그아웃 성공
        refresh_obj = RefreshToken.objects.get(uuid=decoded_refresh_tk["sub"])
        refresh_obj.delete()
        response = Response(
            data={"success": True, "message": "Logout has been processed."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("refreshToken")
        return response
    except RefreshToken.DoesNotExist:
        # 변조 가능성
        return Response(
            data={"success": False, "message": "Does Not Exist this Refresh Token"},
            status=status.HTTP_404_NOT_FOUND,
        )
