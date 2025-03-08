import django_tables2 as tables

from utilities.tables.columns import EditColumn, OpenColumn

from .models import Game, Player, PlayerGroup, Submission, Task


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


class SubmissionTable(tables.Table):
    open = OpenColumn("misterx:submission-detail")
    edit = EditColumn("misterx:submission-edit")

    class Meta:
        model = Submission
        fields = [
            "group",
            "game",
            "task",
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
