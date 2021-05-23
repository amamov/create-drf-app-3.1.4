from django.urls import path
from .views import session as web_views, token as token_views, test as test_views


urlpatterns = [
    path("token/login/", token_views.login),
    path("token/logout/", token_views.logout),
    path("me/", web_views.me, name="me"),
    path("login/", web_views.login),
    path("logout/", web_views.logout),
    path("signup/", web_views.signup, name="signup"),
    path("test/", test_views.TestView.as_view()),
]
