from crispy_forms import layout
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Count, OuterRef, Subquery
from django.utils.translation import gettext_lazy as _

from utilities.templatetags.utilities_media import get_main_mime_type

from .models import Game, OrderedTask, Player, PlayerGroup, Submission, Task


class TaskSelectWidget(forms.SelectMultiple):
    template_name = "generic/task_select_widget.html"

    def __init__(self, *args, game=None, **kwargs):
        self.game = game
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.game.pk:
            selected = self.game.tasks.annotate(
                task_number=Subquery(OrderedTask.objects.filter(game=self.game, task__pk=OuterRef("pk")).values("task_number"))
            ).order_by("task_number")
        else:
            selected = Task.objects.none()
        unselected = Task.objects.exclude(id__in=selected.values_list("id", flat=True))
        context["widget"].update({"selected_tasks": selected, "unselected_tasks": unselected})
        return context


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def single_file_clean(self, data, inital):
        mime_type = get_main_mime_type(data)
        if mime_type not in settings.ALLOWED_UPLOADS:
            raise ValidationError(_("The file type {mime_type} is not supported.").format(mime_type=mime_type))
        return super().clean(data, inital)

    def clean(self, data, initial=None):
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
        self.helper.title = "Game"
        self.helper.add_input(Submit("save", _("Save")))

        self.fields["tasks"].widget = TaskSelectWidget(game=self.instance)

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
        if duplicates := groups.values_list("user").annotate(occurences=Count("id")).exclude(occurences=1):
            raise ValidationError(
                _("These users are present in multiple groups: {users}").format(
                    users=", ".join(str(Player.objects.get(pk=id)) for id, _ in duplicates)
                )
            )
        return groups


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


class SubmissionApproveForm(SubmissionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id_submissionApproveForm"
        self.helper.form_method = "post"
        self.helper.title = "Submission"
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

    def clean_accepted(self):
        return False
