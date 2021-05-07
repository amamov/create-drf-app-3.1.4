from django.urls import path
from .views import cookie as web_views, test as test_views, simple as simple_views


urlpatterns = [
    path("login/", web_views.login_view),
    path("refresh/", web_views.refresh_view),
    path("logout/", web_views.logout_view),
    path("logout/all", web_views.all_logout_view),
    # path("login/", simple_views.login_view),
    # path("logout/", simple_views.logout_view),
    path("test/", test_views.TestView.as_view()),
]
