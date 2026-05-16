from django.db import models
from django.apps import apps
from typing import Any, Dict, List
import json


class GigCategoryManager(models.Manager):
    def get_taxonomy_json(self) -> str:
        """
        Fetches active parent categories and their subcategories, 
        returning a serialized JSON string for frontend use.

        The structure of the returned JSON list is:
        [
            {
                "id": int,
                "name": str,
                "subcategories": [{"id": int, "name": str}, ...]
            },
            ...
        ]

        Returns:
            str: A JSON-encoded string of the hierarchical taxonomy.
        """
        niches:models.QuerySet["GigCategory"] = (
            self.filter(parent__isnull=True, is_active=True)
            .prefetch_related(
                models.Prefetch(
                    "subcategories",
                    queryset=GigCategory.objects.filter(is_active=True).order_by("name"),
                )
            )
            .order_by("name")
        )

        taxonomy:List[Dict[str, Any]] = [
            {
                "id": niche.id,
                "name": niche.name,
                "subcategories": [
                    {"id": sub.id, "name": sub.name}
                    for sub in niche.subcategories.all()
                ],
            }
            for niche in niches
        ]
        return json.dumps(taxonomy)
    

class GigCategory(models.Model):
    """
        Represents a service or business category used to classify gigs and
        role requirements within the marketplace.

        Gig categories define *what type of work* a gig belongs to (e.g.
        Software Development, Graphic Design, Cleaning Services). They are part
        of the global marketplace taxonomy and are reused across gigs, roles,
        and vendor profiles.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Human-readable category name (e.g. Software Development)",
    )

    slug = models.SlugField(
        unique=True,
        help_text="URL-friendly unique identifier for the category",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="subcategories",
        on_delete=models.PROTECT,
        help_text="Optional parent category for hierarchical categorization",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether the category can be used for new gigs",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = GigCategoryManager()

    class Meta:
        db_table = "collaboration_gig_categories"
        verbose_name = "Collaboration/Gig Category"
        verbose_name_plural = "Collaboration/Gig Categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.is_active}"
    
    def is_root(self):
        """
        Returns True if this category is a top-level (parent) category.
        """
        return self.parent is None

    def has_subcategories(self):
        """
        Returns True if this category has one or more subcategories.
        """
        return self.subcategories.exists()

    def active_subcategories(self):
        """
        Returns a queryset of active subcategories for this category.
        """
        return self.subcategories.filter(is_active=True)

    def all_descendants(self):
        """
        Returns a queryset of all descendant categories recursively, including subcategories of subcategories.
        Useful for filtering gigs across an entire category branch.
        """
        descendants = self.subcategories.all()
        for subcat in self.subcategories.all():
            descendants |= subcat.all_descendants()
        return descendants
