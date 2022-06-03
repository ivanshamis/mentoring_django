import jwt

from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from rest_framework import authentication, exceptions

from .models import User


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
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        except Exception as e:
            msg = f"Authentication failed. Unable to decode the token {e}"
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload["id"])
        except User.DoesNotExist:
            msg = "The user corresponding to the given token was not found."
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = "This user is deactivated."
            raise exceptions.AuthenticationFailed(msg)

        return user, token
