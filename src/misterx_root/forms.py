from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import forms as auth_forms
from django.utils.translation import gettext_lazy as _


class LoginForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_loginForm"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Login"), css_class="form-footer w-100"))


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_passwordChangeForm"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("change", _("Change Password"), css_class="form-footer w-100"))


class PasswordResetForm(auth_forms.PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_passwordResetForm"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("reset", _("Reset Password"), css_class="btn btn-danger form-footer w-100"))


class SetPasswordForm(auth_forms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_passwordSetForm"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("Set", _("Set Password"), css_class="form-footer w-100"))
