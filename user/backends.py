import jwt

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache

from rest_framework import authentication, exceptions
from rest_framework.exceptions import AuthenticationFailed

from user.constants import token_expire_hours
from user.models import User


class CustomModelBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Token"

    def authenticate(self, request):
        request.user = None
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) != 2:
            return None

        prefix = auth_header[0].decode("utf-8")
        token = auth_header[1].decode("utf-8")

        if prefix.lower() != auth_header_prefix:
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        try:
            payload = decode_token(token)
        except Exception as e:
            msg = f"Authentication failed. Unable to decode the token {e}"
            raise AuthenticationFailed(msg)

        if payload.get("action") != "login":
            msg = "The token is not intended for login"
            raise AuthenticationFailed(msg)

        try:
            user = get_payload_user(payload)
        except User.DoesNotExist:
            msg = "The user corresponding to the given token was not found."
            raise AuthenticationFailed(msg)

        if not user.is_active:
            msg = "This user is deactivated."
            raise AuthenticationFailed(msg)

        return user, token


def decode_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")


def get_payload_user(payload: dict):
    return User.objects.get(pk=payload["id"])


def validate_token(token: str, action: str):
    if cache.get(token):
        return None

    try:
        payload = decode_token(token)
    except Exception:
        return None

    if payload.get("action") != action:
        return None

    try:
        user = get_payload_user(payload)
    except User.DoesNotExist:
        return None

    cache.set(token, user.pk, 3600 * token_expire_hours[action])

    return user
