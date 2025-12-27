from django.contrib.auth.models import Group, Permission
from django.apps import apps

from .registry import ROLE_PERMISSIONS


def apply_permissions():
    for role, app_perms in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role)

        permissions = []

        for app_label, codenames in app_perms.items():
            if app_label == "*" and codenames == ["*"]:
                permissions.extend(Permission.objects.all())
                continue

            for codename in codenames:
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename,
                    )
                    permissions.append(perm)
                except Permission.DoesNotExist:
                    pass  # fail-safe

        group.permissions.set(permissions)
