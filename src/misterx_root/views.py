from django.conf import settings
from django.shortcuts import redirect


def login_or_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(settings.LOGIN_REDIRECT_URL_STAFF)
        else:
            return redirect(settings.LOGIN_REDIRECT_URL_PLAYER)
    else:
        return redirect("login")
