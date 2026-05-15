from django.db import models
from django.db.models import Sum, Min, Max
from django.db.models.functions import Coalesce
from django.conf import settings
from django.utils import timezone
from uuid6 import uuid7
from .choices import ProposalStatus


class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    project = models.ForeignKey(
        "collaboration.Gig",
        on_delete=models.PROTECT,
        related_name="proposals",
    )

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        to_field="email",
        related_name="proposals",
        help_text="A service provider sending the proposal object"
    )

    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "The worth of the provider's proposal (summation of role amounts). "
            "This is filled during and after the proposal creation or accepted."
        )
    )
    currency = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.SENT,
    )
    sent_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "proposal"
        verbose_name = "Project Proposal"
        verbose_name_plural = "Project Proposals"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["gig", "provider"],
                name="unique_provider_proposal_per_gig",
            )
        ]
        indexes = [
            models.Index(fields=['provider', 'status'], name='proposal_provider_status_idx'),
            models.Index(fields=['gig', 'status'], name='proposal_gig_status_idx'),
            models.Index(fields=['provider', 'gig'], name='provider_proposal__gig_idx'),
        ]
    
    def calculate_total_role_cost(self):
        """
        Calculates the sum of proposed_amounts, falling back to 
        role_amount for each role where proposed_amount is null.
        """
        result = self.roles.aggregate(
            total=Sum(Coalesce('proposed_amount', 'role_amount'))
        )
        return result['total'] or 0.00
    
    def timeline_summary(self):
        deliverables = self.deliverables.order_by("order")

        first = deliverables.first()
        last = deliverables.last()

        if not first or not last:
            return None

        start_date = first.due_date
        end_date = last.due_date

        if not start_date or not end_date:
            return None

        total_days = (end_date - start_date).days

        if total_days == 0:
            return "1 day"

        return self._format_duration(total_days)

    def _format_duration(self, days):
        """Helper to break days into Months, Weeks, and Days"""
        months = days // 30
        remaining_days = days % 30
        
        weeks = remaining_days // 7
        final_days = remaining_days % 7

        parts = []
        if months > 0:
            parts.append(f"{months} month{'s' if months > 1 else ''}")
        if weeks > 0:
            parts.append(f"{weeks} week{'s' if weeks > 1 else ''}")
        if final_days > 0:
            parts.append(f"{final_days} day{'s' if final_days > 1 else ''}")

        return " and ".join(parts) if len(parts) > 1 else parts[0]
    
    
    def get_deliverable_count(self):
        """Returns the total number of deliverables for this proposal."""
        return self.deliverables.count()
    
    def get_role_count(self):
        """returns the total number of roles associated with the proposal"""
        return self.roles.count()
    
    @property
    def sent_ago(self):
        if not self.sent_at:
            return ""

        now = timezone.now()
        diff = now - self.sent_at
        seconds = int(diff.total_seconds())

        # Seconds
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"

        # Minutes
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"

        # Hours
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''}"

        # Days
        days = hours // 24
        if days < 7:
            return f"{days} day{'s' if days != 1 else ''}"

        # Weeks (7–29 days)
        if days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''}"

        # Months (30–364 days)
        if days < 365:
            months = days // 30
            return f"{months} month{'s' if months != 1 else ''}"

        # Years
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''}"