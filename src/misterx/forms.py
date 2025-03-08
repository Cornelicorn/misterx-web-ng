from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Game, Player, PlayerGroup, Submission, Task


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
            "accepted",
            "points_override",
            "explanation",
        ]


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
