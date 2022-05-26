from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from mentoring.serializers import EmptySerializer
from .models import User
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
    AdminSerializer,
)


class AuthViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = EmptySerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=["post"], serializer_class=LoginSerializer)
    def login(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["post"], serializer_class=RegistrationSerializer)
    def signup(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    current_user = "me"

    def get_object(self):
        if self.kwargs.get("pk") == self.current_user:
            return self.request.user
        return super().get_object()

    def update(self, request, *args, **kwargs):
        if self.kwargs["pk"] != self.current_user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class AdminUserViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = AdminSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "create":
            return RegistrationSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
