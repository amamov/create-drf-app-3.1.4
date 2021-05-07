"""
auth api using httponly cookies.
rt, at 모두 httponly cookie에 저장하고 프런트에서는 만료 시간 계산해서 넘겨준다.
"""


import jwt
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
        access_token, exp_timestamp, at_max_age = generate_access_token(user)
        refresh_obj = RefreshToken()
        refresh_token, _, rt_max_age = generate_refresh_token(
            user, request, refresh_obj
        )
        response = Response(
            data={
                "success": True,
                "accessTokenExp": exp_timestamp,
                "user": {"email": email},
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="refreshToken", value=refresh_token, max_age=rt_max_age, httponly=True,
        )
        response.set_cookie(
            key="accessToken", value=access_token, max_age=at_max_age, httponly=True,
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
@authentication_classes([JWTCookieAuthentication])
@permission_classes([IsAuthenticated])
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

    refresh_token, _, rt_max_age = generate_refresh_token(
        refresh_obj.user, request, refresh_obj
    )
    access_token, exp_timestamp, at_max_age = generate_access_token(refresh_obj.user)

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
        key="refreshToken", value=refresh_token, max_age=rt_max_age, httponly=True,
    )
    response.set_cookie(
        key="refreshToken", value=refresh_token, max_age=at_max_age, httponly=True,
    )

    return response


@api_view(["DELETE"])
@authentication_classes([JWTCookieAuthentication])
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
    response.delete_cookie("accessToken")
    return response


@api_view(["POST"])
def logout_view(request):
    """ POST """
    refresh_token = request.COOKIES.get("refreshToken", None)  # refresh token 가져오기

    if not refresh_token:
        return Response(
            data={
                "success": False,
                "message": "The token value was not delivered normally.\
                 (이미 만료된 토큰이거나 토큰이 정상적으로 전달되지 않았습니다.)",
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
        response.delete_cookie("accessToken")
        return response
    except RefreshToken.DoesNotExist:
        # 변조 가능성
        return Response(
            data={"success": False, "message": "Does Not Exist this Refresh Token"},
            status=status.HTTP_404_NOT_FOUND,
        )
