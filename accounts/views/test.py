from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from accounts.authentication import JWTAuthentication
from accounts.permissions import IsAuthenticated


class TestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        response = Response(
            data={
                "status": True,
                "message": "A normally signed token was provided.",
                "user": request.user.email,
            }
        )
        return response
