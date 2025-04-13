from django.urls import path
from .views import (
    ProfileAPIView,
    UserRegisterAPIView,
    InterestUserSearchAPIView,
    HobbyUserSearchAPIView,
    MusicUserSearchAPIView,
    UserIdApiView,
    AvatarSignatureAPIView,
)

urlpatterns = [
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("userid/", UserIdApiView.as_view(), name="id"),
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path(
        "interest-search/", InterestUserSearchAPIView.as_view(), name="interest-search"
    ),
    path("hobby-search/", HobbyUserSearchAPIView.as_view(), name="hobby-search"),
    path("music-search/", MusicUserSearchAPIView.as_view(), name="music-search"),
    path(
        "avatar-signature/", AvatarSignatureAPIView.as_view(), name="avatar-signature"
    ),
]
