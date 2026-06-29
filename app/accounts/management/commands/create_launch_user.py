# accounts/management/commands/create_launch_user.py

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a verified user with pre-launch whitelist access."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email address for the new user.")
        parser.add_argument("--password", required=True, help="Password for the new user.")
        parser.add_argument("--first-name", default="", help="First name (optional).")
        parser.add_argument("--last-name", default="", help="Last name (optional).")
        parser.add_argument("--staff", action="store_true", help="Grant staff/admin access.")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
    
        if User.objects.filter(email=email).exists():
            raise CommandError(f"A user with email '{email}' already exists.")
    
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=options["first_name"],
            last_name=options["last_name"],
            is_staff=options["staff"],
            is_verified=True,
            is_pre_launch_whitelisted=True,
        )
    
        self.stdout.write(self.style.SUCCESS(
            f"✓ User '{user.first_name}' '{user.last_name}' with email '{user.email}' created with pre-launch whitelist access."
            + (" [staff]" if user.is_staff else "")
        ))
        
# Basic user
# python manage.py create_launch_user --email demoacc1@servio.com --password eniol@O20 --first-name Eniola --last-name Olaniyan

# Staff/admin user
# python manage.py create_launch_user --email sammy@servio.com --password securepass123 --staff
