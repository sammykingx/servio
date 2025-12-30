from django.db import models
from django.apps import apps


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

    class Meta:
        db_table = "collaboration_gig_categories"
        verbose_name = "Collaboration/Gig Category"
        verbose_name_plural = "Collaboration/Gig Categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
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


    def gigs_count(self):
        """
        Returns the number of gigs directly associated with this category
        through roles or if the category is assigned directly in future enhancements.
        """
        GigRole = apps.get_model("collaboration", "GigRole")
        return GigRole.objects.filter(niche=self).count()


    def gigs(self):
        """
        Returns a queryset of all gigs associated with this category through roles.
        """
        GigRole = apps.get_model("collaboration", "GigRole")
        Gig = apps.get_model("collaboration", "Gig")
        
        gig_ids = GigRole.objects.filter(niche=self).values_list('gig_id', flat=True)

        return Gig.objects.filter(id__in=gig_ids).distinct()


    def roles(self):
        """
        Returns a queryset of all GigRoles associated with this category.
        """
        GigRole = apps.get_model("collaboration", "GigRole")
        return GigRole.objects.filter(niche=self)


    def top_level_category(self):
        """
        Returns the root parent category for this category.
        If this category is already top-level, returns self.
        """
        category = self
        while category.parent is not None:
            category = category.parent
        return category
