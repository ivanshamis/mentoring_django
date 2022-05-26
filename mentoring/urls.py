from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from user.views import AuthViewSet, UserViewSet, AdminUserViewSet

router = SimpleRouter()
router.register("auth", AuthViewSet, basename="auth")
router.register("user", UserViewSet, basename="user")
router.register("admin", AdminUserViewSet, basename="admin")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((router.urls, "user"), namespace="api")),
]
