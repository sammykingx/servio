from django.core.management.base import BaseCommand
from accounts.permissions.bootstrap import apply_permissions

class Command(BaseCommand):
    help = "Apply centralized role permission registry"

    def handle(self, *args, **options):
        apply_permissions()
        self.stdout.write(self.style.SUCCESS("Permissions applied"))
