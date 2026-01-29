# accounts/management/commands/setup_roles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Setup default user roles and permissions"

    def handle(self, *args, **options):
        role_permissions = {
            "members": [
                "view_booking",
                "add_booking",
            ],
            "providers": [
                "view_booking",
                "change_booking",
            ],
            "staff": [
                "view_booking",
                "change_booking",
                "view_user",
            ],
            "admin": [
                "add_booking",
                "change_booking",
                "delete_booking",
                "view_booking",
                "add_user",
                "change_user",
                "delete_user",
                "view_user",
            ],
        }

        for group_name, perm_codenames in role_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)

            permissions = Permission.objects.filter(
                codename__in=perm_codenames
            )

            group.permissions.set(permissions)

            self.stdout.write(
                self.style.SUCCESS(f"Configured group: {group_name}")
            )
