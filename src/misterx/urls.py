from django.urls import path

from .views import GameListView

urlpatterns = [
    path("games/", GameListView.as_view(), name="game-list")
]

app_name = "misterx"
