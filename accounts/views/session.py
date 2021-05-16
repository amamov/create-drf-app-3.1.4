from django.contrib.auth import login as auth_login, logout as auth_logout
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.serializers import UserSerializer, LoginSerializer


@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    auth_login(request, user)
    return Response(UserSerializer(user).data)


@api_view(["POST"])
def logout(request):
    auth_logout(request)
    return Response()
