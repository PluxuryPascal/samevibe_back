"""
URL configuration for samevibe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from interests.views import (
    InterestsAPIList,
    HobbyAPIList,
    MusicGenreAPIList,
    UserInterestAPIView,
    UserHobbyAPIView,
    UserMusicAPIView,
)
from friends.views import FriendshipAPIList
from users.views import (
    ProfileAPIView,
    UserRegisterAPIView,
    InterestUserSearchAPIView,
    HobbyUserSearchAPIView,
    MusicUserSearchAPIView,
)
from chat.views import ChatAPIView, ChatContentAPIView, ContentRetriveUpdateAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/schema/ui/", SpectacularSwaggerView.as_view()),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/interestslist/", InterestsAPIList.as_view()),
    path("api/v1/hobbylist/", HobbyAPIList.as_view()),
    path("api/v1/musiclist/", MusicGenreAPIList.as_view()),
    path(
        "api/v1/friendshiplist/",
        FriendshipAPIList.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "api/v1/friendship/",
        FriendshipAPIList.as_view({"patch": "update", "delete": "destroy"}),
    ),
    path("api/v1/profile/", ProfileAPIView.as_view()),
    path("api/v1/userinterests/", UserInterestAPIView.as_view()),
    path("api/v1/userhobbies/", UserHobbyAPIView.as_view()),
    path("api/v1/usermusics/", UserMusicAPIView.as_view()),
    path("api/v1/chats/", ChatAPIView.as_view()),
    path(
        "api/v1/chats/<int:chat_id>/messages/",
        ChatContentAPIView.as_view(),
        name="chat-contents",
    ),
    path(
        "api/v1/messages/<int:pk>/",
        ContentRetriveUpdateAPIView.as_view(),
        name="contents-detail",
    ),
    path("api/v1/interest-search/", InterestUserSearchAPIView.as_view()),
    path("api/v1/hobby-search/", HobbyUserSearchAPIView.as_view()),
    path("api/v1/music-search/", MusicUserSearchAPIView.as_view()),
    path("api/v1/register/", UserRegisterAPIView.as_view()),
    # path("", include("chat.urls")),
]
