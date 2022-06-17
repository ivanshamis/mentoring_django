import csv
from datetime import datetime

from django.http import StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_excel.renderers import XLSXRenderer
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_csv.renderers import CSVRenderer

from mentoring.serializers import EmptySerializer
from .backends import validate_token
from .models import User
from .serializers import (
    ActivationSerializer,
    AdminCreateUserSerializer,
    AdminSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordSetupSerializer,
    RegistrationSerializer,
    UserSerializer,
)


class AuthViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = EmptySerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=["post"], serializer_class=LoginSerializer)
    def login(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def logout(self, request, *args, **kwargs):
        validate_token(token=request.auth, action="login", invalidate=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], serializer_class=RegistrationSerializer)
    def signup(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], serializer_class=ActivationSerializer)
    def activate(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["post"], serializer_class=PasswordResetSerializer)
    def password_reset(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["post"], serializer_class=PasswordSetupSerializer)
    def password_setup(self, request, *args, **kwargs):
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


class AdminUserViewSet(ModelViewSet):
    serializer_class = AdminSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email", "first_name", "last_name"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], renderer_classes=([CSVRenderer]))
    def export_csv(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], renderer_classes=([XLSXRenderer]))
    def export_xlsx(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "create":
            return AdminCreateUserSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
