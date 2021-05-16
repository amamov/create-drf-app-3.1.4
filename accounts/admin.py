from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import AccessToken

User = get_user_model()


@admin.register(AccessToken)
class RefreshTokenAdmin(admin.ModelAdmin):

    """ Refresh Token Admin """

    list_display = (
        "user",
        "last_refreshed",
        "device",
        "ip",
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    """ User Admin """

    list_display = ("email",)
    search_fields = ("email",)
