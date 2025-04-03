from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import models
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, SingleTableMixin
from guardian.mixins import LoginRequiredMixin, PermissionListMixin, PermissionRequiredMixin

from utilities.views import InitialCreateView

from .filters import GameFilter, PlayerFilter, PlayerGroupFilter, SubmissionFilter, TaskFilter, UserSubmissionFilter
from .forms import GameForm, GameSubmissionForm, PlayerForm, PlayerGroupForm, SubmissionForm, TaskForm, UserSubmissionForm
from .models import Game, OrderedTask, Player, PlayerGroup, Submission, Task, Upload
from .tables import (
    GamePlayerGroupTable,
    GameTable,
    OrderedTaskTable,
    PlayerGroupTable,
    PlayerTable,
    SubmissionTable,
    TaskTable,
    UserSubmissionTable,
)


class NoActiveGameError(Exception):
    pass


class GameListView(LoginRequiredMixin, PermissionListMixin, SingleTableMixin, FilterView):
    model = Game
    permission_required = "misterx.view_game"
    table_class = GameTable
    template_name = "misterx/game_list.html"
    filterset_class = GameFilter


class GameCreateView(LoginRequiredMixin, PermissionRequiredMixin, InitialCreateView):
    model = Game
    permission_required = "misterx.add_game"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = GameForm


class GameEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Game
    permission_required = "misterx.change_game"
    template_name = "generic/object_edit.html"
    form_class = GameForm


class GameDetailView(LoginRequiredMixin, PermissionRequiredMixin, MultiTableMixin, DetailView):
    model = Game
    permission_required = "misterx.view_game"
    tables = GamePlayerGroupTable, OrderedTaskTable, SubmissionTable

    def get_tables_data(self):
        game = self.get_object()
        groups = PlayerGroupFilter(self.request.GET, game.groups.all(), prefix="groups")
        tasks = TaskFilter(
            self.request.GET,
            game.tasks.annotate(
                task_number=models.Subquery(
                    OrderedTask.objects.filter(game=game, task__pk=models.OuterRef("pk")).values("task_number")
                )
            ).order_by("task_number"),
            prefix="tasks",
        )
        submissions = SubmissionFilter(self.request.GET, game.submissions.all(), prefix="submissions")
        self.filters = groups, tasks, submissions
        return groups.qs, tasks.qs, submissions.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filters": self.filters})
        return context


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


class TaskCreateView(LoginRequiredMixin, PermissionRequiredMixin, InitialCreateView):
    model = Task
    permission_required = "misterx.add_task"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = TaskForm


class TaskEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Task
    permission_required = "misterx.change_task"
    template_name = "generic/object_edit.html"
    form_class = TaskForm


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, MultiTableMixin, DetailView):
    model = Task
    permission_required = "misterx.view_task"
    tables = GameTable, SubmissionTable

    def get_tables_data(self):
        games = GameFilter(self.request.GET, self.get_object().games.all(), prefix="games")
        submissions = SubmissionFilter(self.request.GET, self.get_object().submissions.all(), prefix="submissions")
        self.filters = games, submissions
        return games.qs, submissions.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filters": self.filters})
        return context


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


class SubmissionCreateView(LoginRequiredMixin, PermissionRequiredMixin, InitialCreateView):
    model = Submission
    permission_required = "misterx.add_submission"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = SubmissionForm


class GameSubmissionCreateView(SubmissionCreateView):
    form_class = GameSubmissionForm


class SubmissionEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Submission
    permission_required = "misterx.change_submission"
    template_name = "generic/object_edit.html"
    form_class = SubmissionForm


class SubmissionDetailView(LoginRequiredMixin, PermissionRequiredMixin, MultiTableMixin, DetailView):
    model = Submission
    permission_required = "misterx.view_submission"
    tables = SubmissionTable, SubmissionTable

    def get_tables_data(self):
        obj = self.get_object()
        own_submissions = Submission.objects.filter(game=obj.game, task=obj.task, group=obj.group).exclude(pk=obj.pk)
        other_submissions = Submission.objects.filter(game=obj.game, task=obj.task).exclude(group=obj.group)
        own_submissions_filter = SubmissionFilter(self.request.GET, own_submissions, prefix="own")
        other_submissions_filter = SubmissionFilter(self.request.GET, other_submissions, prefix="other")
        self.filters = own_submissions_filter, other_submissions_filter
        return own_submissions_filter.qs, other_submissions_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filters": self.filters})
        return context


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


class PlayerCreateView(LoginRequiredMixin, PermissionRequiredMixin, InitialCreateView):
    model = Player
    permission_required = "misterx.add_player"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = PlayerForm


class PlayerEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Player
    permission_required = "misterx.change_player"
    template_name = "generic/object_edit.html"
    form_class = PlayerForm


class PlayerDetailView(LoginRequiredMixin, PermissionRequiredMixin, MultiTableMixin, DetailView):
    model = Player
    permission_required = "misterx.view_player"
    tables = PlayerGroupTable, GameTable

    def get_tables_data(self):
        groups = PlayerGroupFilter(self.request.GET, self.get_object().groups.all(), prefix="groups")
        games = GameFilter(self.request.GET, Game.objects.filter(groups__in=groups.qs), prefix="games")
        self.filters = groups, games
        return groups.qs, games.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filters": self.filters})
        return context


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


class PlayerGroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, InitialCreateView):
    model = PlayerGroup
    permission_required = "misterx.add_playergroup"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = PlayerGroupForm


class PlayerGroupEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = PlayerGroup
    permission_required = "misterx.change_playergroup"
    template_name = "generic/object_edit.html"
    form_class = PlayerGroupForm


class PlayerGroupDetailView(LoginRequiredMixin, PermissionRequiredMixin, MultiTableMixin, DetailView):
    model = PlayerGroup
    permission_required = "misterx.view_playergroup"
    tables = PlayerTable, GameTable

    def get_tables_data(self):
        users = PlayerFilter(self.request.GET, self.get_object().user_set.all(), prefix="player")
        games = GameFilter(self.request.GET, self.get_object().games.all(), prefix="games")
        self.filters = users, games
        return users.qs, games.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filters": self.filters})
        return context


class PlayerGroupDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = PlayerGroup
    permission_required = "misterx.delete_playergroup"
    success_url = reverse_lazy("misterx:playergroup-list")
    template_name = "generic/object_confirm_delete.html"


class UserSubmissionView(LoginRequiredMixin, InitialCreateView):
    model = Submission
    template_name = "generic/object_create.html"
    form_class = UserSubmissionForm

    def get_initial(self):
        initial = super().get_initial()
        groups = self.request.user.groups.all()
        try:
            game = Game.objects.filter(groups__in=groups).get(active=True)
        except ObjectDoesNotExist:
            raise NoActiveGameError()
        group = game.groups.intersection(groups).first()
        initial.update({"game": game.pk, "submitter": self.request.user.pk, "group": group.pk})
        return initial

    def get(self, request, *args, **kwargs):
        try:
            resp = super().get(request, *args, **kwargs)
        except NoActiveGameError:
            resp = render(request, "misterx/no_active_game.html")
        return resp

    def get_success_url(self):
        return reverse_lazy("misterx:user-submission-list")

    def form_valid(self, form):
        ret = super().form_valid(form)
        for file in form.cleaned_data["proof"]:
            Upload.objects.create(submission=self.object, file=file)
        return ret


class UserSubmissionListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Submission
    table_class = UserSubmissionTable
    template_name = "misterx/user_submission_list.html"
    filterset_class = UserSubmissionFilter

    def get_queryset(self):
        groups = self.request.user.groups.all()
        try:
            game = Game.objects.filter(groups__in=groups).get(active=True)
        except ObjectDoesNotExist:
            raise NoActiveGameError()
        group = game.groups.intersection(groups).first()
        qs = super().get_queryset()
        qs = qs.filter(game=game, group=group)
        return qs

    def get(self, request, *args, **kwargs):
        try:
            resp = super().get(request, *args, **kwargs)
        except NoActiveGameError:
            resp = render(request, "misterx/no_active_game.html")
        return resp


class UserSubmissionDetailView(LoginRequiredMixin, SingleTableMixin, DetailView):
    model = Submission
    table_class = UserSubmissionTable
    template_name = "misterx/user_submission_detail.html"

    def get_table_data(self):
        obj = self.get_object()
        own_submissions = Submission.objects.filter(game=obj.game, task=obj.task, group=obj.group).exclude(pk=obj.pk)
        own_submissions_filter = UserSubmissionFilter(self.request.GET, own_submissions, prefix="own")
        self.filter = own_submissions_filter
        return own_submissions_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filter": self.filter})
        return context

    def get(self, request, *args, **kwargs):
        if self.get_object().group not in self.request.user.groups.all():
            raise PermissionDenied("You are not in the group of this Submission")
        return super().get(request, *args, **kwargs)
