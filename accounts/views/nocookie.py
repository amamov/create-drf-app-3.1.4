"""
at, rt 모두 로컬 스토리지에 저장
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
            data={"success": False, "message": "Field Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = authenticate(email=email, password=password)
    if user:
        access_token, exp_timestamp, _ = generate_access_token(user)
        refresh_obj = RefreshToken()
        refresh_token, _, max_age = generate_refresh_token(user, request, refresh_obj)
        return Response(
            data={
                "success": True,
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "accessTokenExp": exp_timestamp,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            data={"success": False, "message": "Authentication Error"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def refresh_view(request):
    """ POST {"accessToken", "refreshToken"} """
    access_token = request.data.get("accessToken")
    refresh_token = request.data.get("refreshToken")
    if not access_token and refresh_token:
        return Response(
            data={
                "success": False,
                "message": "The token value was not delivered normally.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        decoded_access_tk = jwt.decode(
            access_token,
            JWT_SECRET_KEY,
            algorithms=JWT_ALGORITHM,
            audience=f"urn:{PROJECT_NAME}:user",
            options={"verify_exp": False},
        )
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

    if str(refresh_obj.user.uuid) != decoded_access_tk["sub"]:
        return Response(
            data={
                "success": False,
                "message": "Access Token and Refresh Token do not match.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh_token, _, max_age = generate_refresh_token(
        refresh_obj.user, request, refresh_obj
    )
    access_token, exp_timestamp, _ = generate_access_token(refresh_obj.user)
    return Response(
        data={
            "success": True,
            "message": "Refresh Success",
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "accessTokenExp": exp_timestamp,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def all_logout_view(request):
    user = request.user
    user.refresh_tokens.all().delete()
    return Response(
        data={
            "success": True,
            "message": "All refresh tokens have been removed, and the user's uuid value has been changed.",
        }
    )


@api_view(["POST"])
def logout_view(request):
    """ POST { "refreshToken" } """
    refresh = request.data.get("refreshToken")

    if not refresh:
        return Response(
            data={
                "success": False,
                "message": "The token value was not delivered normally.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        decoded_refresh_tk = jwt.decode(
            refresh, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM
        )

    except jwt.exceptions.DecodeError:
        return Response(
            data={
                "success": False,
                "message": "The authentication information is invalid or has expired.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not RefreshToken.objects.filter(uuid=decoded_refresh_tk["sub"]).exists:
        return Response(
            data={
                "success": False,
                "message": "No valid authentication information was found. You are already logged out.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
    try:
        refresh_obj = RefreshToken.objects.get(uuid=decoded_refresh_tk["sub"])
        refresh_obj.delete()
        return Response(
            data={"success": True, "message": "Logout has been processed."},
            status=status.HTTP_200_OK,
        )
    except RefreshToken.DoesNotExist:
        return Response(
            data={"success": False, "message": "Does Not Exist this Refresh Token"},
            status=status.HTTP_404_NOT_FOUND,
        )
