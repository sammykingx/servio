from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models.profile import UserProfile, UserRole


class Command(BaseCommand):
    help = "Create default user groups and assign users based on profile roles"

    GROUP_NAMES = [
        UserRole.MEMBERS,
        UserRole.PROVIDERS,
    ]

    def handle(self, *args, **options):
        # 1. Create groups
        groups = {}
        for role in self.GROUP_NAMES:
            group, _ = Group.objects.get_or_create(name=role)
            groups[role] = group
            self.stdout.write(self.style.SUCCESS(f"Group ensured: {role}"))

        # 2. Assign existing users to groups
        profiles = UserProfile.objects.select_related("user")

        for profile in profiles:
            user = profile.user
            user.groups.clear()
            group = groups.get(profile.role)
            if group:
                user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS("Users assigned to groups successfully")
        )
