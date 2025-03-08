from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from guardian.mixins import LoginRequiredMixin, PermissionListMixin, PermissionRequiredMixin

from .filters import GameFilter
from .forms import GameForm
from .models import Game
from .tables import GameTable


class GameListView(LoginRequiredMixin, PermissionListMixin, SingleTableMixin, FilterView):
    model = Game
    permission_required = "misterx.view_game"
    table_class = GameTable
    template_name = "misterx/game_list.html"
    filterset_class = GameFilter

class GameCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Game
    permission_required = "mister.add_game"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = GameForm

class GameEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Game
    permission_required = "mister.change_game"
    template_name = "generic/object_edit.html"
    form_class = GameForm


class GameDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Game
    permission_required = "misterx.view_game"

class GameDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Game
    permission_required = "misterx.delete_game"
    success_url = reverse_lazy("misterx:game-list")
    template_name = "generic/object_confirm_delete.html"
