from django.shortcuts import redirect

from .settings import LOGIN_REDIRECT_URL


def login_or_redirect(request):
    if request.user.is_authenticated:
        return redirect(LOGIN_REDIRECT_URL)
    else:
        return redirect("accounts/login")
