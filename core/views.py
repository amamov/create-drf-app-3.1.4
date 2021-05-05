from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["GET"])
def index(request):
    if settings.DEBUG:
        uri = request.get_raw_uri()
        message = {
            "debug": True,
            "api_name": "amamov api",
            "api_author": "Yoon Sang Seok",
            "api_copyright": "Yoon Sang Seok",
            "api_admin": f"{uri}admin",
            "api_docs": f"{uri}redoc",
            "api_swagger": f"{uri}swagger",
        }
    else:
        message = {
            "api_name": "amamov api",
            "api_author": "Yoon Sang Seok",
            "api_copyright": "Yoon Sang Seok",
        }
    return Response(data=message, status=status.HTTP_200_OK)
