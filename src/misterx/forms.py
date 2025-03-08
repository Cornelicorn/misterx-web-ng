from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Game


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
