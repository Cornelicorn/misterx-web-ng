from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import models, transaction
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, UpdateView
from django.views.static import serve
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, SingleTableMixin
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin

from utilities.views import InitialCreateView

from .filters import (
    GameFilter,
    PlayerFilter,
    PlayerGroupFilter,
    SubmissionFilter,
    TaskFilter,
    UserSubmissionFilter,
    UserTaskFilter,
)
from .forms import (
    GameForm,
    GameSubmissionForm,
    PlayerForm,
    PlayerGroupForm,
    SubmissionApproveForm,
    SubmissionForm,
    TaskForm,
    UserSubmissionForm,
)
from .models import Game, OrderedTask, Player, PlayerGroup, Submission, Task, Upload, get_players_in_multiple_groups
from .tables import (
    GamePlayerGroupTable,
    GameTable,
    OrderedTaskTable,
    PlayerGroupTable,
    PlayerTable,
    SubmissionTable,
    TaskTable,
    UserSubmissionTable,
    UserTaskTable,
)


class NoActiveGameError(Exception):
    pass


class NoUnreviewedSubmissions(Exception):
    pass


class SubmissionAlreadyReviewed(Exception):
    pass


class PlayerInMultipleGroupsError(Exception):
    def __init__(self, game, groups):
        super().__init__()
        self.game = game
        self.groups = groups


class PlayerGameMixin:
    """
    Provides the active game and group of the requesting player and shows a notice instead of the view if the
    player doesn't participate in a game or is in more than one group of it
    """

    def get_group(self, game):
        groups = list(game.groups.filter(user=self.request.user))
        if len(groups) > 1:
            raise PlayerInMultipleGroupsError(game, groups)
        return groups[0] if groups else None

    def get_game_and_group(self):
        game = Game.objects.filter(active=True, groups__user=self.request.user).first()
        if game is None:
            raise NoActiveGameError()
        return game, self.get_group(game)

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except NoActiveGameError:
            return render(request, "misterx/no_active_game.html")
        except PlayerInMultipleGroupsError as e:
            return render(request, "misterx/player_in_multiple_groups.html", {"game": e.game, "groups": e.groups})


class MultipleGroupsWarningMixin:
    """
    Warns about players who are in more than one group of the games of get_games_to_check(), as they can't see
    anything of these games until they are in only one of their groups
    """

    def get_games_to_check(self):
        return Game.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["players_in_multiple_groups"] = get_players_in_multiple_groups(self.get_games_to_check())
        return context


class FilteredMultiTableMixin(MultiTableMixin):
    """
    Provides the filters of the tables to the template, get_tables_data() has to store them in self.filters.
    The columns of fields left out of a filter with exclude are hidden as well, as they have the same value in
    every row.
    """

    def get_tables(self):
        tables = super().get_tables()
        for table, filterset in zip(tables, self.filters):
            table.exclude = (*table.exclude, *getattr(filterset, "excluded", ()))
        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filters": self.filters})
        return context


class RelatedSubmissionsMixin(FilteredMultiTableMixin):
    """
    Lists the other submissions of the group and the submissions of the other groups for the task of the submission
    """

    tables = SubmissionTable, SubmissionTable

    def get_tables_data(self):
        obj = self.object
        own_submissions = Submission.objects.filter(game=obj.game, task=obj.task, group=obj.group).exclude(pk=obj.pk)
        other_submissions = Submission.objects.filter(game=obj.game, task=obj.task).exclude(group=obj.group)
        own_submissions_filter = SubmissionFilter(
            self.request.GET, own_submissions, prefix="own", exclude=["group", "game", "task"]
        )
        other_submissions_filter = SubmissionFilter(
            self.request.GET, other_submissions, prefix="other", exclude=["game", "task"]
        )
        self.filters = own_submissions_filter, other_submissions_filter
        return own_submissions_filter.qs, other_submissions_filter.qs


class GameListView(LoginRequiredMixin, PermissionRequiredMixin, MultipleGroupsWarningMixin, SingleTableMixin, FilterView):
    model = Game
    permission_required = "misterx.view_game"
    permission_object = None
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


class GameDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, MultipleGroupsWarningMixin, FilteredMultiTableMixin, DetailView
):
    model = Game
    permission_required = "misterx.view_game"
    tables = GamePlayerGroupTable, OrderedTaskTable, SubmissionTable

    def get_games_to_check(self):
        return Game.objects.filter(pk=self.object.pk)

    def get_tables_data(self):
        game = self.object
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
        submissions = SubmissionFilter(self.request.GET, game.submissions.all(), prefix="submissions", exclude=["game"])
        self.filters = groups, tasks, submissions
        return groups.qs, tasks.qs, submissions.qs


class GameDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Game
    permission_required = "misterx.delete_game"
    success_url = reverse_lazy("misterx:game-list")
    template_name = "generic/object_confirm_delete.html"


class TaskListView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableMixin, FilterView):
    model = Task
    permission_required = "misterx.view_task"
    permission_object = None
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


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, FilteredMultiTableMixin, DetailView):
    model = Task
    permission_required = "misterx.view_task"
    tables = GameTable, SubmissionTable

    def get_tables_data(self):
        games = GameFilter(self.request.GET, self.object.games.all(), prefix="games")
        submissions = SubmissionFilter(self.request.GET, self.object.submissions.all(), prefix="submissions", exclude=["task"])
        self.filters = games, submissions
        return games.qs, submissions.qs


class TaskDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Task
    permission_required = "misterx.delete_task"
    success_url = reverse_lazy("misterx:task-list")
    template_name = "generic/object_confirm_delete.html"


class SubmissionListView(LoginRequiredMixin, PermissionRequiredMixin, MultipleGroupsWarningMixin, SingleTableMixin, FilterView):
    model = Submission
    permission_required = "misterx.view_submission"
    permission_object = None
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

    # The "Add Submission" button of a game passes the game and group in the query string
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            game = Game.objects.get(pk=self.request.GET.get("game"))
            group = game.groups.get(pk=self.request.GET.get("group"))
        except (ObjectDoesNotExist, ValueError):
            raise Http404()
        kwargs["instance"] = Submission(game=game, group=group)
        return kwargs


class SubmissionEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Submission
    permission_required = "misterx.change_submission"
    template_name = "generic/object_edit.html"
    form_class = SubmissionForm


class SubmissionDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, MultipleGroupsWarningMixin, RelatedSubmissionsMixin, DetailView
):
    model = Submission
    permission_required = "misterx.view_submission"

    def get_games_to_check(self):
        return Game.objects.filter(pk=self.object.game_id)


class SubmissionApproveView(
    LoginRequiredMixin, PermissionRequiredMixin, MultipleGroupsWarningMixin, RelatedSubmissionsMixin, UpdateView
):
    model = Submission
    form_class = SubmissionApproveForm
    permission_required = "misterx.change_submission"
    permission_object = None
    template_name = "misterx/submission_approve.html"

    # Only submissions of the active game are reviewed
    def get_games_to_check(self):
        return Game.objects.filter(active=True)

    def get_object(self, queryset=None):
        try:
            game = Game.objects.get(active=True)
        except ObjectDoesNotExist:
            raise NoActiveGameError()

        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.filter(game=game, accepted=None)

        # A specific submission is requested when a decision is posted for the submission the reviewer
        # was shown. Someone else might have reviewed it in the meantime, so only take it if it is still
        # unreviewed and lock it until the decision is saved.
        if "pk" in self.kwargs:
            if self.request.method == "POST":
                queryset = queryset.select_for_update()
            obj = queryset.filter(pk=self.kwargs["pk"]).first()
            if obj is None:
                raise SubmissionAlreadyReviewed
            return obj

        obj = queryset.first()
        if obj is None:
            raise NoUnreviewedSubmissions
        return obj

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except NoActiveGameError:
            return render(request, "misterx/no_active_game.html", {"for_staff": True})
        except NoUnreviewedSubmissions:
            # Players in more than one group can't submit anything, so they might be why there is nothing to review
            players = get_players_in_multiple_groups(self.get_games_to_check())
            return render(request, "misterx/no_unreviewed_submissions.html", {"players_in_multiple_groups": players})
        except SubmissionAlreadyReviewed:
            return render(request, "misterx/submission_already_reviewed.html")

    # Decisions always have to name the reviewed submission, see get_object()
    def post(self, request, *args, **kwargs):
        if "pk" not in kwargs:
            return self.http_method_not_allowed(request, *args, **kwargs)
        with transaction.atomic():
            return super().post(request, *args, **kwargs)

    # Cycle back to the same view every time
    def get_success_url(self):
        return reverse_lazy("misterx:submission-approve")

    # Handle two submission buttons, one for accepting, one for denying
    def form_valid(self, form):
        if self.request.POST.get("deny"):
            form.instance.accepted = False
        if self.request.POST.get("accept"):
            form.instance.accepted = True

        return super().form_valid(form)


class SubmissionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Submission
    permission_required = "misterx.delete_submission"
    success_url = reverse_lazy("misterx:submission-list")
    template_name = "generic/object_confirm_delete.html"


class PlayerListView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableMixin, FilterView):
    model = Player
    permission_required = "auth.view_user"
    permission_object = None
    table_class = PlayerTable
    template_name = "misterx/player_list.html"
    filterset_class = PlayerFilter


class PlayerCreateView(LoginRequiredMixin, PermissionRequiredMixin, InitialCreateView):
    model = Player
    permission_required = "auth.add_user"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = PlayerForm


class PlayerEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Player
    permission_required = "auth.change_user"
    template_name = "generic/object_edit.html"
    form_class = PlayerForm


class PlayerDetailView(LoginRequiredMixin, PermissionRequiredMixin, FilteredMultiTableMixin, DetailView):
    model = Player
    permission_required = "auth.view_user"
    tables = PlayerGroupTable, GameTable

    def get_tables_data(self):
        groups = PlayerGroupFilter(self.request.GET, PlayerGroup.objects.filter(user=self.object), prefix="groups")
        games = GameFilter(self.request.GET, Game.objects.filter(groups__in=groups.qs), prefix="games")
        self.filters = groups, games
        return groups.qs, games.qs


class PlayerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Player
    permission_required = "auth.delete_user"
    success_url = reverse_lazy("misterx:player-list")
    template_name = "generic/object_confirm_delete.html"


class PlayerGroupListView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableMixin, FilterView):
    model = PlayerGroup
    permission_required = "auth.view_group"
    permission_object = None
    table_class = PlayerGroupTable
    template_name = "misterx/playergroup_list.html"
    filterset_class = PlayerGroupFilter


class PlayerGroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, InitialCreateView):
    model = PlayerGroup
    permission_required = "auth.add_group"
    permission_object = None
    template_name = "generic/object_create.html"
    form_class = PlayerGroupForm


class PlayerGroupEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = PlayerGroup
    permission_required = "auth.change_group"
    template_name = "generic/object_edit.html"
    form_class = PlayerGroupForm


class PlayerGroupDetailView(LoginRequiredMixin, PermissionRequiredMixin, FilteredMultiTableMixin, DetailView):
    model = PlayerGroup
    permission_required = "auth.view_group"
    tables = PlayerTable, GameTable

    def get_tables_data(self):
        users = PlayerFilter(self.request.GET, Player.objects.filter(groups=self.object), prefix="player")
        games = GameFilter(self.request.GET, self.object.games.all(), prefix="games")
        self.filters = users, games
        return users.qs, games.qs


class PlayerGroupDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = PlayerGroup
    permission_required = "auth.delete_group"
    success_url = reverse_lazy("misterx:playergroup-list")
    template_name = "generic/object_confirm_delete.html"


class UserSubmissionView(LoginRequiredMixin, PlayerGameMixin, InitialCreateView):
    model = Submission
    template_name = "generic/object_create.html"
    form_class = UserSubmissionForm

    # The player only chooses the task, everything else about the submission is set here
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        game, group = self.get_game_and_group()
        kwargs["instance"] = Submission(game=game, group=group, submitter_id=self.request.user.pk)
        return kwargs

    def get_success_url(self):
        return reverse_lazy("misterx:user-submission-list")

    def form_valid(self, form):
        ret = super().form_valid(form)
        for file in form.cleaned_data["proof"]:
            Upload.objects.create(submission=self.object, file=file)
        return ret


class UserSubmissionListView(LoginRequiredMixin, PlayerGameMixin, SingleTableMixin, FilterView):
    model = Submission
    table_class = UserSubmissionTable
    template_name = "misterx/user_submission_list.html"
    filterset_class = UserSubmissionFilter

    def get_queryset(self):
        game, group = self.get_game_and_group()
        qs = super().get_queryset()
        qs = qs.filter(game=game, group=group)
        return qs


class UserSubmissionDetailView(LoginRequiredMixin, PlayerGameMixin, SingleTableMixin, DetailView):
    model = Submission
    table_class = UserSubmissionTable
    template_name = "misterx/user_submission_detail.html"

    def get_table_data(self):
        obj = self.object
        own_submissions = Submission.objects.filter(game=obj.game, task=obj.task, group=obj.group).exclude(pk=obj.pk)
        own_submissions_filter = UserSubmissionFilter(self.request.GET, own_submissions, prefix="own", exclude=["task"])
        self.filter = own_submissions_filter
        return own_submissions_filter.qs

    # Hide the columns left out of the filter like FilteredMultiTableMixin
    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        table.exclude = self.filter.excluded
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"filter": self.filter})
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.groups.filter(pk=obj.group_id).exists():
            raise PermissionDenied("You are not in the group of this Submission")
        # Players in more than one group of the game must not see anything of it
        self.get_group(obj.game)
        return obj


class UserTaskListView(LoginRequiredMixin, PlayerGameMixin, SingleTableMixin, FilterView):
    model = Task
    table_class = UserTaskTable
    template_name = "misterx/user_task_list.html"
    filterset_class = UserTaskFilter

    def get_queryset(self):
        game, group = self.get_game_and_group()
        qs = (
            super()
            .get_queryset()
            .filter(pk__in=game.tasks.all().values_list("pk", flat=True))
            .annotate(
                task_number=models.Subquery(
                    OrderedTask.objects.filter(game=game, task__pk=models.OuterRef("pk")).values("task_number")
                )
            )
            .annotate(submitted=models.Exists(Submission.objects.filter(game=game, group=group, task__pk=models.OuterRef("pk"))))
            .order_by("submitted", "task_number")
        )
        return qs


def serve_proofs(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        # Fetch upload object for the file
        try:
            upload = Upload.objects.get(file=request.path.removeprefix(settings.MEDIA_URL))
        except ObjectDoesNotExist:
            raise PermissionDenied()

        # Check if user is in the group of the submission or if they are staff
        # Otherwise return 403
        allowed_group = upload.submission.group
        if allowed_group not in user.groups.all() and not user.is_staff:
            raise PermissionDenied()

        # Finally, serve the file
        if settings.DEBUG:
            return serve(request, *args, **kwargs)
        else:
            response = HttpResponse()
            response["Content-Type"] = ""
            response["X-Accel-Redirect"] = "/protected_media/" + request.path
            return response
    else:
        raise PermissionDenied()
