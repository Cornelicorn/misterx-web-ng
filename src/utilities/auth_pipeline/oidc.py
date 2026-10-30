from django.conf import settings


def assign_attributes(backend, user, response, *args, **kwargs):
    """
    Grant admin rights based on the OIDC groups claim. The groups themselves aren't synced, as all Django groups
    are playergroups.
    """
    if backend.name == "oidc":
        groups = response.get("groups", [])

        if settings.ADMIN_GROUP is not None:
            if settings.ADMIN_GROUP in groups:
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False

        user.full_clean()
        user.save()
