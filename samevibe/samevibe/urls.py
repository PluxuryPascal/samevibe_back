from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/schema/ui/", SpectacularSwaggerView.as_view()),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/interests/", include("interests.urls")),
    path("api/v1/friends/", include("friends.urls")),
    path("api/v1/chat/", include("chat.urls")),
]
