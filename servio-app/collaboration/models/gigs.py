"""
Gig domain model.

This module defines the `Gig` model, which represents a project or gig listing
created within the marketplace. A gig is the top-level container for work being
requested and serves as the parent entity for role requirements, applications,
and assignments.

A gig describes:
- Who created the work request
- What type of service or domain the work belongs to
- The visibility and lifecycle status of the listing
- The overall scope, timeline, and estimated budget

Specific roles, skills, and staffing needs for a gig are modeled separately
using related role-requirement models (e.g. `GigRole`).

Indexes:
    - Composite index on (status, visibility) to optimize common discovery and
      filtering queries.
    - Index on creator to optimize creator-based filtering.

Ordering:
    Gigs are ordered by creation date in descending order by default.
"""


from django.db import models
from django.conf import settings
from uuid6 import uuid7
from .choices import GigVisibility, GigStatus


class Gig(models.Model):
    """
        Represents a project or gig listing within the marketplace.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        to_field="email",
        related_name="gigs",
    )

    title = models.CharField(max_length=350)
    visibility = models.CharField(
        max_length=30,
        choices=GigVisibility.choices,
        default=GigVisibility.PUBLIC
    )

    status = models.CharField(
        max_length=30,
        choices=GigStatus.choices,
        default=GigStatus.DRAFT
    )

    description = models.TextField()

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    total_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Overall estimated budget"
    )
    
    is_negotiable = models.BooleanField(
        default=False,
        help_text="Indicates if the total budget is negotiable"
    )
    has_gig_roles = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "collaboration_gigs"
        verbose_name = "Collaboration/Gigs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "visibility"]),
            models.Index(fields=["creator"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.creator.email}, {self.status})"
    
    def is_active(self):
        """
            Returns True if the gig is published and still ongoing.
        """
        return self.status == GigStatus.PUBLISHED

    def duration(self):
        """
            Returns the duration of the gig in days, if both start_date and end_date are set.
            Returns None if dates are not fully specified.
        """
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

    def role_count(self):
        """
            Returns the number of roles associated with this gig.
            Assumes a related_name 'roles' exists in the GigRole model.
        """
        return getattr(self, 'roles', self.required_roles).count()
    
    def total_role_budget(self):
        """
            Returns the total budget allocated to all roles in this gig.
            Efficiently sums the 'budget * quantity' for all related roles in the database.
        """
        from django.db.models import F, Sum
        result = self.required_roles.aggregate(
            total=Sum(F('budget') * F('quantity'))
        )
        return result['total'] or 0

    def open_role_count(self):
        """
            Returns the number of roles that are currently open (not assigned or completed).
        """
        return self.required_roles.filter(status='open').count()

    def assigned_role_count(self):
        """
            Returns the number of roles that have been assigned.
        """
        return self.required_roles.filter(status='assigned').count()

    def total_workload_summary(self):
        """
            Returns a summary of roles by workload type as a dictionary.
            Example: {'fixed_hours': 3, 'flexible': 2, 'professional_discretion': 1}
        """
        from django.db.models import Count
        qs = self.required_roles.values('workload').annotate(count=Count('id'))
        return {item['workload']: item['count'] for item in qs}

    def top_level_categories(self):
        """
        Returns a list of unique top-level categories (parents) for all roles in this gig.
        Useful for displaying the main categories of the gig.
        """
        return self.required_roles.filter(
            niche__parent__isnull=False
        ).values_list('niche__parent__name', flat=True).distinct()
    