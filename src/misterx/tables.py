import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from tabler_ui.tables import ButtonColumn, EditColumn, OpenColumn

from .models import Game, Player, PlayerGroup, Submission, Task


class AddSubmissionForGroupColumn(ButtonColumn):
    def __init__(self, verbose_name: str = _("Add Submission")):
        super().__init__("misterx/tables/columns/add_group_submission.html", "misterx:game-submission-create", verbose_name)


class AddSubmissionForTaskColumn(ButtonColumn):
    def __init__(self, verbose_name: str = _("Submit")):
        super().__init__("misterx/tables/columns/add_user_task_submission.html", "misterx:user-submission-create", verbose_name)


class GameTable(tables.Table):
    open = OpenColumn("misterx:game-detail")
    edit = EditColumn("misterx:game-edit")

    class Meta:
        model = Game
        fields = [
            "name",
            "date",
            "open",
            "edit",
        ]


class TaskTable(tables.Table):
    open = OpenColumn("misterx:task-detail")
    edit = EditColumn("misterx:task-edit")

    class Meta:
        model = Task
        fields = [
            "task",
            "points",
            "solution",
            "open",
            "edit",
        ]


class OrderedTaskTable(TaskTable):
    task_number = tables.Column(verbose_name=_("Task number"), attrs={"th": {"class": "w-1"}})

    class Meta:
        model = Task
        fields = [
            "task_number",
            "task",
            "points",
            "solution",
            "open",
            "edit",
        ]


class UserTaskTable(tables.Table):
    task_number = tables.Column(verbose_name=_("Task number"), attrs={"th": {"class": "w-1"}})
    submitted = tables.BooleanColumn(verbose_name=_("Submitted"))
    add = AddSubmissionForTaskColumn()

    class Meta:
        model = Task
        fields = [
            "task_number",
            "task",
            "points",
            "submitted",
        ]


class SubmissionTable(tables.Table):
    open = OpenColumn("misterx:submission-detail")
    edit = EditColumn("misterx:submission-edit")
    granted_points = tables.Column(verbose_name=_("Granted points"), orderable=False)

    class Meta:
        model = Submission
        fields = [
            "group",
            "game",
            "task",
            "submitter",
            "time",
            "accepted",
            "granted_points",
            "explanation",
            "feedback",
            "open",
            "edit",
        ]


class PlayerTable(tables.Table):
    open = OpenColumn("misterx:player-detail")
    edit = EditColumn("misterx:player-edit")

    class Meta:
        model = Player
        fields = [
            "username",
            "first_name",
            "last_name",
        ]


class PlayerGroupTable(tables.Table):
    open = OpenColumn("misterx:playergroup-detail")
    edit = EditColumn("misterx:playergroup-edit")

    class Meta:
        model = PlayerGroup
        fields = [
            "name",
        ]


class GamePlayerGroupTable(tables.Table):
    open = OpenColumn("misterx:playergroup-detail")
    edit = EditColumn("misterx:playergroup-edit")
    add = AddSubmissionForGroupColumn()

    class Meta:
        model = PlayerGroup
        fields = [
            "name",
            "add",
        ]


class UserSubmissionTable(tables.Table):
    open = OpenColumn("misterx:user-submission-detail")
    granted_points = tables.Column(verbose_name=_("Granted points"), orderable=False)

    class Meta:
        model = Submission
        fields = [
            "task",
            "submitter",
            "time",
            "accepted",
            "granted_points",
            "explanation",
            "feedback",
        ]
