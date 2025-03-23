import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from utilities.tables.columns import EditColumn, OpenColumn

from .models import Game, Player, PlayerGroup, Submission, Task


class AddSubmissionColumn(tables.TemplateColumn):
    def __init__(self, verbose_name: str = _("Add Submission")):
        super().__init__(
            template_name="misterx/tables/columns/add_submission.html",
            verbose_name=verbose_name,
            attrs={
                "td": {"align": "right"},
                "th": {"style": "text-align: right;", "class": "w-1"},
            },
            orderable=False,
        )
        self.extra_context.update({"url_target": "misterx:game-submission-create"})


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


class SubmissionTable(tables.Table):
    open = OpenColumn("misterx:submission-detail")
    edit = EditColumn("misterx:submission-edit")

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
    add = AddSubmissionColumn()

    class Meta:
        model = PlayerGroup
        fields = [
            "name",
            "add",
        ]
