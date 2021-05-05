from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
    path("v1/users/", include("accounts.urls")),
]


if settings.DEBUG:
    import debug_toolbar
    from django.urls import re_path
    from django.conf.urls.static import static
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    schema_view = get_schema_view(
        openapi.Info(
            title="amamov api",
            default_version="v1",
            description="amamov API V1",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(name="amamov", email="amamov@kakao.com"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    urlpatterns += (
        [
            path("api-auth/", include("rest_framework.urls")),
            re_path(
                r"^swagger(?P<format>\.json|\.yaml)$",
                schema_view.without_ui(cache_timeout=0),
                name="schema-json",
            ),
            re_path(
                r"^swagger/$",
                schema_view.with_ui("swagger", cache_timeout=0),
                name="schema-swagger-ui",
            ),
            re_path(
                r"^redoc/$",
                schema_view.with_ui("redoc", cache_timeout=0),
                name="schema-redoc",
            ),
        ]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + [path("__debug__/", include(debug_toolbar.urls))]
    )
