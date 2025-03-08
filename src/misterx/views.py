from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from guardian.mixins import LoginRequiredMixin, PermissionListMixin, PermissionRequiredMixin

from .filters import GameFilter, PlayerFilter, PlayerGroupFilter, SubmissionFilter, TaskFilter
from .forms import GameForm, PlayerForm, PlayerGroupForm, SubmissionForm, TaskForm
from .models import Game, Player, PlayerGroup, Submission, Task
from .tables import GameTable, PlayerGroupTable, PlayerTable, SubmissionTable, TaskTable


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


class TaskListView(LoginRequiredMixin, PermissionListMixin, SingleTableMixin, FilterView):
    model = Task
    permission_required = "misterx.view_task"
    table_class = TaskTable
    template_name = "misterx/task_list.html"
    filterset_class = TaskFilter


class TaskCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Task
    permission_required = "mister.add_task"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = TaskForm


class TaskEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Task
    permission_required = "mister.change_task"
    template_name = "generic/object_edit.html"
    form_class = TaskForm


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Task
    permission_required = "misterx.view_task"


class TaskDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Task
    permission_required = "misterx.delete_task"
    success_url = reverse_lazy("misterx:task-list")
    template_name = "generic/object_confirm_delete.html"


class SubmissionListView(LoginRequiredMixin, PermissionListMixin, SingleTableMixin, FilterView):
    model = Submission
    permission_required = "misterx.view_submission"
    table_class = SubmissionTable
    template_name = "misterx/submission_list.html"
    filterset_class = SubmissionFilter


class SubmissionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Submission
    permission_required = "mister.add_submission"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = SubmissionForm


class SubmissionEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Submission
    permission_required = "mister.change_submission"
    template_name = "generic/object_edit.html"
    form_class = SubmissionForm


class SubmissionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Submission
    permission_required = "misterx.view_submission"


class SubmissionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Submission
    permission_required = "misterx.delete_submission"
    success_url = reverse_lazy("misterx:submission-list")
    template_name = "generic/object_confirm_delete.html"


class PlayerListView(LoginRequiredMixin, PermissionListMixin, SingleTableMixin, FilterView):
    model = Player
    permission_required = "misterx.view_player"
    table_class = PlayerTable
    template_name = "misterx/player_list.html"
    filterset_class = PlayerFilter


class PlayerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Player
    permission_required = "mister.add_player"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = PlayerForm


class PlayerEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Player
    permission_required = "mister.change_player"
    template_name = "generic/object_edit.html"
    form_class = PlayerForm


class PlayerDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Player
    permission_required = "misterx.view_player"


class PlayerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Player
    permission_required = "misterx.delete_player"
    success_url = reverse_lazy("misterx:player-list")
    template_name = "generic/object_confirm_delete.html"


class PlayerGroupListView(LoginRequiredMixin, PermissionListMixin, SingleTableMixin, FilterView):
    model = PlayerGroup
    permission_required = "misterx.view_playergroup"
    table_class = PlayerGroupTable
    template_name = "misterx/playergroup_list.html"
    filterset_class = PlayerGroupFilter


class PlayerGroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = PlayerGroup
    permission_required = "mister.add_playergroup"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = PlayerGroupForm


class PlayerGroupEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = PlayerGroup
    permission_required = "mister.change_playergroup"
    template_name = "generic/object_edit.html"
    form_class = PlayerGroupForm


class PlayerGroupDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = PlayerGroup
    permission_required = "misterx.view_playergroup"


class PlayerGroupDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = PlayerGroup
    permission_required = "misterx.delete_playergroup"
    success_url = reverse_lazy("misterx:playergroup-list")
    template_name = "generic/object_confirm_delete.html"
