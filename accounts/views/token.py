import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.permissions import IsAuthenticated
from accounts.jwt import generate_access_token
from accounts.models import AccessToken

User = get_user_model()
PROJECT_NAME = settings.JWT_AUTH["PROJECT_NAME"]
JWT_SECRET_KEY = settings.JWT_AUTH["JWT_SECRET_KEY"]
JWT_ALGORITHM = settings.JWT_AUTH["JWT_ALGORITHM"]


@api_view(["POST"])
def login(request):
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
        token_obj = AccessToken()
        access_token, exp_timestamp = generate_access_token(user, request, token_obj)
        return Response(
            data={
                "success": True,
                "accessToken": access_token,
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
@permission_classes([IsAuthenticated])
def logout(request):
    """ POST { "token" } """
    try:
        token = AccessToken.objects.filter(user=request.user)
        token.delete()
        return Response(
            data={"success": True, "message": "Logout has been processed."},
            status=status.HTTP_200_OK,
        )
    except AccessToken.DoesNotExist:
        return Response(
            data={"success": False, "message": "Does Not Exist this Token"},
            status=status.HTTP_404_NOT_FOUND,
        )
