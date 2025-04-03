from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .models import Game, OrderedTask, Player, PlayerGroup, Submission, Task


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, list | tuple):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class FilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.add_input(Submit("submit", _("Filter"), css_class="w-100"))


class GameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_gameForm"
        self.helper.form_method = "post"
        self.helper.title = "Game"
        self.helper.add_input(Submit("save", _("Save")))

    class Meta:
        model = Game
        fields = [
            "name",
            "date",
            "active",
            "groups",
            "tasks",
        ]


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_taskForm"
        self.helper.form_method = "post"
        self.helper.title = "Task"
        self.helper.add_input(Submit("save", _("Save")))

    class Meta:
        model = Task
        fields = [
            "task",
            "points",
            "solution",
        ]


class SubmissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_submissionForm"
        self.helper.form_method = "post"
        self.helper.title = "Submission"
        self.helper.add_input(Submit("save", _("Save")))

    class Meta:
        model = Submission
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


class GameSubmissionForm(SubmissionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in "game", "group", "accepted", "explanation", "feedback":
            self.fields[field].widget = forms.HiddenInput()

        # Limit displayed tasks to the tasks in the given game
        game = Game.objects.get(pk=kwargs.get("initial").get("game"))
        self.fields["task"].choices = (
            (t.task.id, str(t)) for t in OrderedTask.objects.filter(game=game, task__in=game.tasks.all())
        )
        # Limit displayed submitters to the ones in the given group
        group = PlayerGroup.objects.get(pk=kwargs.get("initial").get("group"))
        self.fields["submitter"].choices = group.user_set.all().values_list("pk", "username")


class PlayerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_playerForm"
        self.helper.form_method = "post"
        self.helper.title = "Player"
        self.helper.add_input(Submit("save", _("Save")))

    class Meta:
        model = Player
        fields = [
            "username",
            "first_name",
            "last_name",
            "is_active",
            "groups",
        ]

    def clean_groups(self):
        data = self.cleaned_data["groups"]
        if duplicates := data.values_list("games").annotate(occurences=Count("id")).exclude(occurences=1):
            raise ValidationError(
                _("The selected groups conflict in these games: {games}").format(
                    games=", ".join(str(Game.objects.get(pk=id)) for id, _ in duplicates)
                )
            )
        return data


class PlayerGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_playerGroupForm"
        self.helper.form_method = "post"
        self.helper.title = "Playergroup"
        self.helper.add_input(Submit("save", _("Save")))

    class Meta:
        model = PlayerGroup
        fields = [
            "name",
        ]


class UserSubmissionForm(SubmissionForm):
    proof = MultipleFileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in "game", "group", "accepted", "submitter", "points_override", "feedback":
            self.fields[field].widget = forms.HiddenInput()

        # Limit displayed tasks to the tasks in the given game
        game = Game.objects.get(pk=kwargs.get("initial").get("game"))
        self.fields["task"].choices = (
            (t.task.id, str(t)) for t in OrderedTask.objects.filter(game=game, task__in=game.tasks.all())
        )
