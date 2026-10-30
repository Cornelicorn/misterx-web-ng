from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter, ChoiceFilter, FilterSet

from .forms import FilterForm
from .models import Game, Player, PlayerGroup, Submission, Task


class ExcludeFilterSet(FilterSet):
    """
    Leaves out the filters of the fields given in exclude, which have the same value for all objects, e.g. the game
    of the submissions of a game. FilteredMultiTableMixin also hides their columns.
    """

    def __init__(self, *args, exclude=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.excluded = tuple(exclude)
        for name in self.excluded:
            del self.filters[name]


class GameFilter(FilterSet):
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Game
        form = FilterForm
        fields = [
            "name",
            "date",
        ]


class TaskFilter(FilterSet):
    task = CharFilter(lookup_expr="icontains")
    solution = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Task
        form = FilterForm
        fields = [
            "task",
            "points",
            "solution",
        ]


class UserTaskFilter(FilterSet):
    task = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Task
        form = FilterForm
        fields = [
            "task",
            "points",
        ]


class SubmissionFilter(ExcludeFilterSet):
    accepted = ChoiceFilter(null_label=_("Unreviewed"), choices=((True, _("Yes")), (False, _("No"))))
    explanation = CharFilter(lookup_expr="icontains")
    feedback = CharFilter(lookup_expr="icontains")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in "group", "game", "task", "submitter":
            if field in self.filters:
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
            "accepted",
            "points_override",
            "explanation",
            "feedback",
        ]


class PlayerFilter(FilterSet):
    username = CharFilter(lookup_expr="icontains")
    first_name = CharFilter(lookup_expr="icontains")
    last_name = CharFilter(lookup_expr="icontains")

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
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = PlayerGroup
        form = FilterForm
        fields = [
            "name",
        ]


class UserSubmissionFilter(ExcludeFilterSet):
    accepted = ChoiceFilter(null_label=_("Unreviewed"), choices=((True, _("Yes")), (False, _("No"))))
    explanation = CharFilter(lookup_expr="icontains")
    feedback = CharFilter(lookup_expr="icontains")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in "task", "submitter":
            if field in self.filters:
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
            "explanation",
            "feedback",
        ]
