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
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.utils.formats import date_format
from uuid6 import uuid7
from .choices import GigVisibility, GigStatus
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta


class Gig(models.Model):
    """
        Represents a project or gig listing within the marketplace.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    slug = models.SlugField(
        max_length=580,
        unique=True,
        editable=False,
        db_index=True
    )
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
    is_active = models.BooleanField(default=True)
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
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:250]
            self.slug = f"{base}-{uuid7().hex[:12]}"
        super().save(*args, **kwargs)
    
    def is_active(self):
        """
            Returns True if the gig is published and still ongoing.
        """
        return self.status == GigStatus.PUBLISHED

    def duration(self):
        
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
        
    @property
    def updated_display(self):
        now = timezone.now()
        delta = now - self.updated_at

        if delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

        if delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"

        if delta.days == 1:
            return f"yesterday {date_format(self.updated_at, 'P')}"

        return date_format(self.updated_at, "M j, Y")
    
    @property
    def gig_duration(self):
        """
            Returns the duration of the gig in days, if both start_date and end_date are set.
        """
        if not self.start_date or not self.end_date:
            return None

        delta = relativedelta(self.end_date, self.start_date)
        parts = []

        if delta.months:
            parts.append(f"{delta.months} months")
        if delta.days:
            parts.append(f"{delta.days} days")

        return ", ".join(parts)
    
    @property
    def all_applications(self):
        return [
            application
            for role in self.required_roles.all()
            for application in role.applications.all()
        ]
    
    @property
    def service_fee(self):
        return (
            self.total_budget * Decimal("0.05")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @property   
    def tax(self):
        return (
            self.total_budget * Decimal("0.07")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def total_amount_payable(self):
        return (
            self.total_budget + self.service_fee + self.tax
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    