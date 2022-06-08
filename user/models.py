import uuid

import jwt

from datetime import datetime, timedelta

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.db import models
from django.urls import reverse

from user.constants import ErrorMessages, email_templates, token_expire_hours
from user.message_sender import email_sender


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError(ErrorMessages.USER_MUST_HAVE_USERNAME)

        if email is None:
            raise TypeError(ErrorMessages.USER_MUST_HAVE_EMAIL)

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError(ErrorMessages.SUPERUSER_MUST_HAVE_PASSWORD)

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=False)
    last_name = models.CharField(max_length=100, null=True, blank=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token(
            hours=token_expire_hours["login"], action="login"
        )

    @property
    def activate_token(self):
        return self._generate_jwt_token(
            hours=token_expire_hours["activate"], action="activate"
        )

    @property
    def activation_url(self):
        return f"{settings.SITE_URL}{reverse('api:auth-activate')}?token={self.activate_token}"

    @property
    def password_token(self):
        return self._generate_jwt_token(
            hours=token_expire_hours["password"], action="password"
        )

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def _generate_jwt_token(self, hours: int, action: str):
        dt = datetime.now() + timedelta(hours=hours)

        token = jwt.encode(
            {
                "id": str(self.pk),
                "action": action,
                "exp": int(dt.strftime("%s")),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return token


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        email_sender.send_message(
            instance, email_templates.get_activation_message(instance)
        )
