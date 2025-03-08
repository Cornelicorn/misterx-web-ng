from misterx_root.settings import SOCIAL_AUTH_OIDC_OIDC_ENDPOINT


def read_settings(request):
    use_sso = bool(SOCIAL_AUTH_OIDC_OIDC_ENDPOINT)
    return {"use_sso": use_sso}
