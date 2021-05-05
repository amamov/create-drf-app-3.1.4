from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password):
        if not email:
            raise ValueError("Email is Required.")
        user = self.model(email=email)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.model(email=email, date_joined=timezone.now())
        user.set_password(password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    """ User Model """

    objects = UserManager()

    uuid = models.UUIDField(
        primary_key=True, default=uuid4, null=False, blank=False, auto_created=True,
    )
    email = models.EmailField(max_length=254, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["username"]


class RefreshToken(models.Model):

    """ Refresh Token Model """

    uuid = models.UUIDField(primary_key=True, default=uuid4, null=False, blank=False)
    last_refreshed = models.DateTimeField(default=timezone.now, null=False, blank=False)
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
        null=False,
        blank=False,
    )
    device = models.TextField(null=True, blank=True)
    ip = models.GenericIPAddressField(unpack_ipv4=True, protocol="both")

    def __str__(self):
        return str(self.user)
