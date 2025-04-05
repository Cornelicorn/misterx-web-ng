from django_filters import ChoiceFilter, FilterSet

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


class UserTaskFilter(FilterSet):
    class Meta:
        model = Task
        form = FilterForm
        fields = [
            "task",
            "points",
        ]


class SubmissionFilter(FilterSet):
    accepted = ChoiceFilter(null_label="Unreviewed", choices=((True, "Yes"), (False, "No")))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in "group", "game", "task", "submitter":
            self.filters[field].queryset = (
                self.filters[field].queryset.filter(id__in=self.queryset.values_list(field, flat=True)).distinct()
            )

    class Meta:
        model = Submission
        form = FilterForm
        fields = [
            "group",
            "game",
            "task",
            "submitter",
            "time",
            "accepted",
            "points_override",
            "explanation",
            "feedback",
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


class UserSubmissionFilter(FilterSet):
    accepted = ChoiceFilter(null_label="Unreviewed", choices=((True, "Yes"), (False, "No")))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in "task", "submitter":
            self.filters[field].queryset = (
                self.filters[field].queryset.filter(id__in=self.queryset.values_list(field, flat=True)).distinct()
            )

    class Meta:
        model = Submission
        form = FilterForm
        fields = [
            "task",
            "submitter",
            "accepted",
            "points_override",
            "explanation",
            "feedback",
        ]
