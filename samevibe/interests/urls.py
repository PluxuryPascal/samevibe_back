from django.urls import path
from .views import (
    InterestsAPIList,
    HobbyAPIList,
    MusicGenreAPIList,
    UserInterestAPIView,
    UserHobbyAPIView,
    UserMusicAPIView,
)

urlpatterns = [
    path("interestslist/", InterestsAPIList.as_view(), name="interests-list"),
    path("hobbylist/", HobbyAPIList.as_view(), name="hobby-list"),
    path("musiclist/", MusicGenreAPIList.as_view(), name="music-list"),
    path("userinterests/", UserInterestAPIView.as_view(), name="user-interests"),
    path("userhobbies/", UserHobbyAPIView.as_view(), name="user-hobbies"),
    path("usermusics/", UserMusicAPIView.as_view(), name="user-musics"),
]
