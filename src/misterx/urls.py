from django.urls import path

from .views import GameListView, GameCreateView, GameDetailView, GameEditView, GameDeleteView

urlpatterns = [
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/create", GameCreateView.as_view(), name="game-create"),
    path("games/<slug:pk>", GameDetailView.as_view(), name="game-detail"),
    path("games/<slug:pk>/edit", GameEditView.as_view(), name="game-edit"),
    path("games/<slug:pk>/delete", GameDeleteView.as_view(), name="game-delete"),
]

app_name = "misterx"
