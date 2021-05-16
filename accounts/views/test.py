from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication


class TestView(APIView):
    authentication_classes = [SessionAuthentication]
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
