from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    GameCreateView,
    GameDeleteView,
    GameDetailView,
    GameEditView,
    GameListView,
    GameSubmissionCreateView,
    PlayerCreateView,
    PlayerDeleteView,
    PlayerDetailView,
    PlayerEditView,
    PlayerGroupCreateView,
    PlayerGroupDeleteView,
    PlayerGroupDetailView,
    PlayerGroupEditView,
    PlayerGroupListView,
    PlayerListView,
    SubmissionApproveView,
    SubmissionCreateView,
    SubmissionDeleteView,
    SubmissionDetailView,
    SubmissionEditView,
    SubmissionListView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskEditView,
    TaskListView,
    UserSubmissionDetailView,
    UserSubmissionListView,
    UserSubmissionView,
    UserTaskListView,
    serve_proofs,
)

urlpatterns = [
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/addsubmission", GameSubmissionCreateView.as_view(), name="game-submission-create"),
    path("games/create", GameCreateView.as_view(), name="game-create"),
    path("games/<slug:pk>", GameDetailView.as_view(), name="game-detail"),
    path("games/<slug:pk>/edit", GameEditView.as_view(), name="game-edit"),
    path("games/<slug:pk>/delete", GameDeleteView.as_view(), name="game-delete"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/create", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<slug:pk>", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<slug:pk>/edit", TaskEditView.as_view(), name="task-edit"),
    path("tasks/<slug:pk>/delete", TaskDeleteView.as_view(), name="task-delete"),
    path("submissions/", SubmissionListView.as_view(), name="submission-list"),
    path("submissions/approve", SubmissionApproveView.as_view(), name="submission-approve"),
    path("submissions/create", SubmissionCreateView.as_view(), name="submission-create"),
    path("submissions/<slug:pk>", SubmissionDetailView.as_view(), name="submission-detail"),
    path("submissions/<slug:pk>/edit", SubmissionEditView.as_view(), name="submission-edit"),
    path("submissions/<slug:pk>/delete", SubmissionDeleteView.as_view(), name="submission-delete"),
    path("players/", PlayerListView.as_view(), name="player-list"),
    path("players/create", PlayerCreateView.as_view(), name="player-create"),
    path("players/<slug:pk>", PlayerDetailView.as_view(), name="player-detail"),
    path("players/<slug:pk>/edit", PlayerEditView.as_view(), name="player-edit"),
    path("players/<slug:pk>/delete", PlayerDeleteView.as_view(), name="player-delete"),
    path("playergroups/", PlayerGroupListView.as_view(), name="playergroup-list"),
    path("playergroups/create", PlayerGroupCreateView.as_view(), name="playergroup-create"),
    path("playergroups/<slug:pk>", PlayerGroupDetailView.as_view(), name="playergroup-detail"),
    path("playergroups/<slug:pk>/edit", PlayerGroupEditView.as_view(), name="playergroup-edit"),
    path("playergroups/<slug:pk>/delete", PlayerGroupDeleteView.as_view(), name="playergroup-delete"),
    path("user/tasks/", UserTaskListView.as_view(), name="user-task-list"),
    path("user/submit/", UserSubmissionView.as_view(), name="user-submission-create"),
    path("user/submissions/", UserSubmissionListView.as_view(), name="user-submission-list"),
    path("user/submissions/<slug:pk>", UserSubmissionDetailView.as_view(), name="user-submission-detail"),
] + static(settings.MEDIA_URL, view=serve_proofs, document_root=settings.MEDIA_ROOT)

app_name = "misterx"
