from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.static import serve

from .settings import LOGIN_REDIRECT_URL, LOGIN_REDIRECT_URL_STAFF


def login_or_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(LOGIN_REDIRECT_URL_STAFF)
        else:
            return redirect(LOGIN_REDIRECT_URL)
    else:
        return redirect("accounts/login")


def serve_protected_media(request, *args, **kwargs):
    if request.user.is_authenticated:
        if settings.DEBUG:
            return serve(request, *args, **kwargs)
        else:
            response = HttpResponse()
            response['Content-Type'] = ''
            response['X-Accel-Redirect'] = request.path
            return response
    else:
        return HttpResponse(status=403)
