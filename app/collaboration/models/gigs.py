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
from constants import SERVICE_FEE, GST_TAX_FEE, DECIMAL_PLACE
from uuid6 import uuid7
from .choices import ProjectVisibility, ProjectStatus
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta


class Gig(models.Model):
    """
        Represents a project or gig listing within the marketplace.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    slug = models.SlugField(
        max_length=230,
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
        choices=ProjectVisibility.choices,
        default=ProjectVisibility.PUBLIC
    )

    status = models.CharField(
        max_length=30,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT
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
        help_text="Indicates if the client is open to negotiation on the budget"
    )
    has_gig_roles = models.BooleanField(default=True)
    is_gig_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gigs_and_projects"
        verbose_name = "Collaboration/Gigs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "visibility"]),
            models.Index(fields=["creator"]),
            models.Index(fields=["status", "visibility", "is_gig_active"])
        ]

    def __str__(self):
        return f"{self.title} ({self.creator.email}, {self.status})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:220]
            self.slug = f"{base}-{uuid7().hex[:12]}"
        super().save(*args, **kwargs)
    
    def is_active(self):
        """
            Returns True if the gig is published and still ongoing.
        """
        return self.status == ProjectStatus.PUBLISHED

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
            Efficiently sums the 'budget * slots' for all related roles in the database.
        """
        from django.db.models import F, Sum
        result = self.required_roles.aggregate(
            total=Sum(F('budget') * F('slots'))
        )
        return result['total'] or 0

    # @property
    # def active_proposals_count(self):
    #     return self.proposals.count()
    
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
            Returns the duration of the project in days, if both start_date and end_date are set.
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
    def service_fee(self):
        return (
            self.total_budget * Decimal(str(SERVICE_FEE))
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
    
    @property   
    def tax(self):
        return (
            self.total_budget * Decimal(str(GST_TAX_FEE))
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)

    @property
    def total_amount_payable(self):
        return (
            self.total_budget + self.service_fee + self.tax
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
        
    @property
    def dynamic_range(self):
        lower_raw = self.total_budget * Decimal('0.6')
        upper_raw = self.total_budget * Decimal('1.1')

        lower = (lower_raw / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10
        upper = (upper_raw / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10

        min_limit = Decimal('50')
        display_lower = max(lower, min_limit)

        return f"${display_lower:,.0f} - ${upper:,.0f}"
    
    # ------ contracts related methods ----------
    @property
    def pending_provider_acceptance_count(self) -> int:
        """
        Returns count of contracts where the provider has not yet accepted terms.
        Uses the prefetched 'all_contracts' if available to save DB hits.
        """
        contracts = getattr(self, 'all_contracts', self.contracts.all())
        return sum(1 for c in contracts if not c.provider_accepted_terms_at)

    @property
    def active_contracts_count(self) -> int:
        """Counts only contracts currently in the 'activated' status."""
        contracts = getattr(self, 'all_contracts', self.contracts.all())
        # Assuming your Enum is ContractStatus.ACTIVATED
        return sum(1 for c in contracts if c.status == "activated")

    @property
    def signed_contracts_count(self) -> int:
        """Counts contracts that are signed but maybe not yet fully 'activated'."""
        contracts = getattr(self, 'all_contracts', self.contracts.all())
        return sum(1 for c in contracts if c.status == "signed")
    