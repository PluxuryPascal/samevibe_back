from django.urls import path
from .views import FriendshipAPIList

urlpatterns = [
    path(
        "friendshiplist/",
        FriendshipAPIList.as_view({"get": "list", "post": "create"}),
        name="friendship-list",
    ),
    path(
        "friendship/",
        FriendshipAPIList.as_view({"patch": "update", "delete": "destroy"}),
        name="friendship-detail",
    ),
]
