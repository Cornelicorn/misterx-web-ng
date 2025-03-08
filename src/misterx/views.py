from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from guardian.mixins import LoginRequiredMixin, PermissionListMixin

from .filters import GameFilter
from .models import Game
from .tables import GameTable


class GameListView(LoginRequiredMixin, PermissionListMixin, SingleTableMixin, FilterView):
    model = Game
    permission_required = "misterx.view_game"
    table_class = GameTable
    template_name = "misterx/game_list.html"
    filterset_class = GameFilter
