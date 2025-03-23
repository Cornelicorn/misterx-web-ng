from django.shortcuts import redirect

from .settings import LOGIN_REDIRECT_URL, LOGIN_REDIRECT_URL_STAFF


def login_or_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(LOGIN_REDIRECT_URL_STAFF)
        else:
            return redirect(LOGIN_REDIRECT_URL)
    else:
        return redirect("accounts/login")
