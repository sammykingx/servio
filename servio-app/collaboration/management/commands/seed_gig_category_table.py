from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
from collaboration.data.gig_roles_categories import GIGS_ROLES_CATEGORIES


GigCategory = apps.get_model("collaboration", "GigCategory")


class Command(BaseCommand):
    help = "Seed gig categories and subcategories"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding gig categories..."))

        created_count = 0
        updated_count = 0

        for category_data in GIGS_ROLES_CATEGORIES:
            parent, created = GigCategory.objects.get_or_create(
                slug=category_data["slug"],
                defaults={
                    "name": category_data["name"],
                    "parent": None,
                    "is_active": True,
                },
            )

            if not created and parent.name != category_data["name"]:
                parent.name = category_data["name"]
                parent.save(update_fields=["name"])
                updated_count += 1

            if created:
                created_count += 1

            # Subcategories
            for sub in category_data.get("subcategories", []):
                child, child_created = GigCategory.objects.get_or_create(
                    slug=sub["slug"],
                    defaults={
                        "name": sub["name"],
                        "parent": parent,
                        "is_active": True,
                    },
                )

                if not child_created:
                    needs_update = False

                    if child.name != sub["name"]:
                        child.name = sub["name"]
                        needs_update = True

                    if child.parent_id != parent.id:
                        child.parent = parent
                        needs_update = True

                    if needs_update:
                        child.save(update_fields=["name", "parent"])
                        updated_count += 1

                else:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding complete. Created: {created_count}, Updated: {updated_count}"
            )
        )
