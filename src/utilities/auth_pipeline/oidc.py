from django.conf import settings
from django.contrib.auth.models import Group


def assign_groups_and_attributes(backend, user, response, *args, **kwargs):
    """
    Assign Django groups based on OIDC claims.
    """
    print(f"{backend.name=}")
    if backend.name == "oidc":
        groups = response.get("groups", [])

        for group_name in groups:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        if settings.ADMIN_GROUP is not None:
            if settings.ADMIN_GROUP in groups:
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False

        user.full_clean()
        user.save()
