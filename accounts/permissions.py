from rest_framework.permissions import BasePermission


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
