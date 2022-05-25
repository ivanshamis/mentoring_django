from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from mentoring.serializers import EmptySerializer
from .models import User
from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer


class AuthViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = EmptySerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=["post"], serializer_class=LoginSerializer)
    def login(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["post"], serializer_class=RegistrationSerializer)
    def signup(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"])
    def me(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.user.pk
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# class RegistrationAPIView(APIView):
#     permission_classes = (AllowAny,)
#     serializer_class = RegistrationSerializer
#     renderer_classes = (UserJSONRenderer,)
#
#     def post(self, request):
#         user = request.data.get("user", {})
#
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# class LoginAPIView(APIView):
#     permission_classes = (AllowAny,)
#     renderer_classes = (UserJSONRenderer,)
#     serializer_class = LoginSerializer
#
#     def post(self, request):
#         user = request.data.get("user", {})
#
#         # Обратите внимание, что мы не вызываем метод save() сериализатора, как
#         # делали это для регистрации. Дело в том, что в данном случае нам
#         # нечего сохранять. Вместо этого, метод validate() делает все нужное.
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
#     permission_classes = (IsAuthenticated,)
#     renderer_classes = (UserJSONRenderer,)
#     serializer_class = UserSerializer
#
#     def retrieve(self, request, *args, **kwargs):
#         # Здесь нечего валидировать или сохранять. Мы просто хотим, чтобы
#         # сериализатор обрабатывал преобразования объекта User во что-то, что
#         # можно привести к json и вернуть клиенту.
#         serializer = self.serializer_class(request.user)
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def update(self, request, *args, **kwargs):
#         serializer_data = request.data.get("user", {})
#
#         # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
#         serializer = self.serializer_class(
#             request.user, data=serializer_data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
