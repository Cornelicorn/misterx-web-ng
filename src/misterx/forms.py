from crispy_forms import layout
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from utilities.templatetags.utilities_media import get_main_mime_type

from .models import Game, OrderedTask, Player, PlayerGroup, Submission, Task


def get_task_choices(game: Game) -> list[tuple[int, str]]:
    return [(t.task_id, str(t)) for t in OrderedTask.objects.filter(game=game).select_related("task")]


class TaskSelectWidget(forms.SelectMultiple):
    template_name = "generic/task_select_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Show the selected tasks in the order of the value, which is the order of the saved game or,
        # if the form is shown again because it was invalid, the submitted order
        selected_ids = [int(pk) for pk in context["widget"]["value"] if pk.isdigit()]
        tasks = Task.objects.in_bulk(selected_ids)
        selected = [tasks[pk] for pk in selected_ids if pk in tasks]
        unselected = Task.objects.exclude(id__in=tasks.keys())
        context["widget"].update({"selected_tasks": selected, "unselected_tasks": unselected})
        return context


class AcceptedSelect(forms.NullBooleanSelect):
    """Calls submissions which haven't been accepted or denied yet "Unreviewed" instead of "Unknown" """

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = [("unknown", _("Unreviewed")), ("true", _("Yes")), ("false", _("No"))]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def single_file_clean(self, data, initial):
        mime_type = get_main_mime_type(data)
        if mime_type not in settings.ALLOWED_UPLOADS:
            raise ValidationError(_("The file type {mime_type} is not supported.").format(mime_type=mime_type))
        return super().clean(data, initial)

    def clean(self, data, initial=None):
        # Without any files the single file checks never run, so check required here
        if not data:
            if self.required:
                raise ValidationError(self.error_messages["required"], code="required")
            return []
        if isinstance(data, list | tuple):
            result = [self.single_file_clean(d, initial) for d in data]
        else:
            result = [self.single_file_clean(data, initial)]
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
        self.helper.title = _("Game")
        self.helper.add_input(Submit("save", _("Save")))

        self.fields["tasks"].widget = TaskSelectWidget()
        if self.instance.pk:
            self.initial["tasks"] = list(OrderedTask.objects.filter(game=self.instance).values_list("task_id", flat=True))

    def save(self, commit=True):
        # Save the game first including all m2m relationships
        game = super().save(commit=commit)

        # Update order, only possible if the m2m relationships exist, which is the case
        # if we have commited them just above
        if commit:
            for index, task_id in enumerate(self.data.getlist("tasks")):
                ordered_task = OrderedTask.objects.get(game=game, task_id=task_id)
                ordered_task.task_number = index + 1
                ordered_task.full_clean()
                ordered_task.save()

        return game

    class Meta:
        model = Game
        fields = [
            "name",
            "date",
            "active",
            "groups",
            "tasks",
        ]

    # Check if any user is present in multiple of the selected groups
    def clean_groups(self):
        groups = self.cleaned_data["groups"]
        duplicates = (
            groups.filter(user__isnull=False).values_list("user").annotate(occurrences=Count("id")).exclude(occurrences=1)
        )
        if duplicates:
            raise ValidationError(
                _("These users are present in multiple groups: {users}").format(
                    users=", ".join(str(Player.objects.get(pk=user_id)) for user_id, _count in duplicates)
                )
            )
        return groups


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_taskForm"
        self.helper.form_method = "post"
        self.helper.title = _("Task")
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
        self.helper.title = _("Submission")
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
        widgets = {"accepted": AcceptedSelect}


class SubmissionApproveForm(SubmissionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_submissionApproveForm"
        self.helper.form_method = "post"
        # Post the decision for this submission, not for whatever is first in line when submitting
        self.helper.form_action = reverse("misterx:submission-approve", kwargs={"pk": self.instance.pk})
        self.helper.title = _("Submission")
        self.helper.add_input(Submit("deny", _("Deny"), css_class="btn btn-danger w-25"))
        self.helper.add_input(Submit("accept", _("Accept"), css_class="btn btn-success w-25 float-end"))

        self.helper.layout = layout.Layout(
            layout.Div(
                layout.Div("points_override", css_class="col-md-2"),
                layout.Div("feedback", css_class="col-md-10"),
                css_class="row",
            )
        )
        # Add default points for task as placeholder in override
        self.fields["points_override"].widget.attrs.update({"placeholder": self.instance.task.points})
        self.fields["feedback"].widget.attrs.update({"rows": 1})

    class Meta:
        model = Submission
        fields = [
            "points_override",
            "feedback",
        ]


class GameSubmissionForm(SubmissionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in "accepted", "explanation", "feedback":
            self.fields[field].widget = forms.HiddenInput()

        group = self.instance.group
        self.helper.title = _("Submission for {group}").format(group=group)
        # Limit displayed tasks to the tasks in the game and submitters to the players in the group
        self.fields["task"].choices = get_task_choices(self.instance.game)
        self.fields["submitter"].choices = group.user_set.all().values_list("pk", "username")

    # Game and group are set by the view
    class Meta:
        model = Submission
        fields = [
            "task",
            "submitter",
            "accepted",
            "points_override",
            "explanation",
            "feedback",
        ]


class PlayerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_playerForm"
        self.helper.form_method = "post"
        self.helper.title = _("Player")
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
        duplicates = (
            data.filter(games__isnull=False).values_list("games").annotate(occurrences=Count("id")).exclude(occurrences=1)
        )
        if duplicates:
            raise ValidationError(
                _("The selected groups conflict in these games: {games}").format(
                    games=", ".join(str(Game.objects.get(pk=game_id)) for game_id, _count in duplicates)
                )
            )
        return data


class PlayerGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_playerGroupForm"
        self.helper.form_method = "post"
        self.helper.title = _("Playergroup")
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

        # Limit displayed tasks to the tasks in the game of the submission
        self.fields["task"].choices = get_task_choices(self.instance.game)

    # Game, group and submitter are set by the view and new submissions stay unreviewed, they must not
    # be form fields, as players could change them in the submitted data otherwise.
    class Meta:
        model = Submission
        fields = [
            "task",
            "explanation",
        ]
