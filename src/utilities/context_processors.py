from django.conf import settings


def read_settings(request):
    use_sso = bool(settings.SOCIAL_AUTH_OIDC_OIDC_ENDPOINT)
    return {"use_sso": use_sso}
