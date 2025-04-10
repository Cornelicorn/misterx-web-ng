import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from utilities.tables.columns import EditColumn, OpenColumn

from .models import Game, Player, PlayerGroup, Submission, Task


class AddSubmissionForGroupColumn(tables.TemplateColumn):
    def __init__(self, verbose_name: str = _("Add Submission")):
        super().__init__(
            template_name="misterx/tables/columns/add_group_submission.html",
            verbose_name=verbose_name,
            attrs={
                "td": {"align": "right"},
                "th": {"style": "text-align: right;", "class": "w-1"},
            },
            orderable=False,
        )
        self.extra_context.update({"url_target": "misterx:game-submission-create"})


class AddSubmissionForTaskColumn(tables.TemplateColumn):
    def __init__(self, verbose_name: str = _("Submit")):
        super().__init__(
            template_name="misterx/tables/columns/add_user_task_submission.html",
            verbose_name=verbose_name,
            attrs={
                "td": {"align": "right"},
                "th": {"style": "text-align: right;", "class": "w-1"},
            },
            orderable=False,
        )
        self.extra_context.update({"url_target": "misterx:user-submission-create"})


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
    per_page = 1

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
    task_number = tables.Column(attrs={"th": {"class": "w-1"}})

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
    task_number = tables.Column(attrs={"th": {"class": "w-1"}})
    completed = tables.BooleanColumn()
    add = AddSubmissionForTaskColumn()

    class Meta:
        model = Task
        fields = [
            "task_number",
            "task",
            "points",
            "completed",
        ]


class SubmissionTable(tables.Table):
    open = OpenColumn("misterx:submission-detail")
    edit = EditColumn("misterx:submission-edit")
    granted_points = tables.Column(orderable=False)

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
    granted_points = tables.Column(orderable=False)

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
