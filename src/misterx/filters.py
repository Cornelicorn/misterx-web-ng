from django_filters import FilterSet

from .forms import FilterForm
from .models import Game, Player, PlayerGroup, Submission, Task


class GameFilter(FilterSet):
    class Meta:
        model = Game
        form = FilterForm
        fields = [
            "name",
            "date",
        ]


class TaskFilter(FilterSet):
    class Meta:
        model = Task
        form = FilterForm
        fields = [
            "task",
            "points",
            "solution",
        ]


class SubmissionFilter(FilterSet):
    class Meta:
        model = Submission
        form = FilterForm
        fields = [
            "group",
            "game",
            "task",
            "time",
            "accepted",
            "points_override",
            "explanation",
        ]


class PlayerFilter(FilterSet):
    class Meta:
        model = Player
        form = FilterForm
        fields = [
            "username",
            "first_name",
            "last_name",
            "is_active",
        ]


class PlayerGroupFilter(FilterSet):
    class Meta:
        model = PlayerGroup
        form = FilterForm
        fields = [
            "name",
        ]
