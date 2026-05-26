from django.db import models
from django.utils.functional import cached_property
from collaboration.models.choices import PaymentOption
from .choices import ProposalRoleStatus,DurationUnit
from decimal import Decimal, ROUND_HALF_UP
from uuid6 import uuid7


class ProposalRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    proposal = models.ForeignKey(
        "Proposal",
        on_delete=models.CASCADE,
        related_name="roles",
    )

    role = models.ForeignKey(
        "collaboration.GigRole",
        on_delete=models.PROTECT,
        related_name="proposal_roles_by_gig_role",
        blank=True,
        null=True,
        help_text="the project role this bid is for (scoped projects)",
    )
    
    category = models.ForeignKey(
        "collaboration.GigCategory",
        on_delete=models.PROTECT,
        related_name="proposal_roles_by_category",
        blank=True,
        null=True,
        help_text="Link to a GigCategory if it's an open project."
    )
    role_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Human friendly role title (e.g. Senior Frontend Engineer). This is used for open projects where the provider can specify the role title they are applying for."
    )
    description = models.TextField(blank=True, null=True)
    client_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The amount stated by client (scoped project)"
    )

    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Provider's asking price, independent of client budget"
    )
    currency = models.CharField(max_length=10)

    payment_plan = models.CharField(
        max_length=20,
        choices=PaymentOption.choices,
        help_text="Provider's preferred installment structure"
    )
    
    status = models.CharField(
        max_length=20,
        choices=ProposalRoleStatus.choices,
        default=ProposalRoleStatus.PENDING,
    )
    created_at = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = "proposal_roles"
        verbose_name = "Proposal Role"
        verbose_name_plural = "Proposal Roles"
        
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.role and self.category:
            raise ValidationError("A ProposalRole can only have either a role or a category, not both.")
        if not self.role and not self.category:
            raise ValidationError("A ProposalRole must have either a role or a category, not both.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    # @property
    # def role_name(self):
    #     """
    #     Returns the name of the role, whether it's from a GigRole or a GigCategory.
    #     This makes template rendering simple.
    #     """
    #     if self.role:
    #         return self.role.role_name
    #     elif self.category:
    #         return self.category.name
    #     return "Unknown Role"
    
    @property
    def applied_role(self):
        if self.role:
            return self.role_id
        
        return self.category_id
    
    @property
    def client_budget_range(self):
        amount = self.client_budget
        lower_raw = amount * Decimal('0.6')
        upper_raw = amount * Decimal('1.1')

        lower = (lower_raw / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10
        upper = (upper_raw / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10

        min_limit = Decimal('50')
        display_lower = max(lower, min_limit)

        return f"${display_lower:,.0f} - ${upper:,.0f}"
    
    @cached_property
    def estimated_timeline(self) -> str:
        """
        Calculates the total timeline by converting all related deliverables 
        to days, summing them, and breaking them down cleanly into 
        Months, Weeks, and Days based on business logic limits.
        """
        # Prefetching avoids N+1 queries if you call this in a loop or template
        deliverables = self.deliverables.all()
        if not deliverables:
            return "0 days"

        total_days = 0
        
        # 1. Normalize everything to Days
        for d in deliverables:
            if d.duration_unit == DurationUnit.DAYS:
                total_days += d.duration_value
            elif d.duration_unit == DurationUnit.WEEKS:
                total_days += d.duration_value * 7
            elif d.duration_unit == DurationUnit.MONTHS:
                total_days += d.duration_value * 30

        # 2. Convert back to optimized, human-readable units
        months = total_days // 30
        remaining_days = total_days % 30
        
        weeks = remaining_days // 7
        days = remaining_days % 7

        # 3. Format the output string based on your scale limits
        parts = []
        if months > 0:
            parts.append(f"{months} month{'s' if months > 1 else ''}")
        if weeks > 0:
            parts.append(f"{weeks} week{'s' if weeks > 1 else ''}")
        if days > 0:
            parts.append(f"{days} day{'s' if days > 1 else ''}")

        return ", ".join(parts) if parts else "0 days"
    
    def count_deliverable(self):
        """Returns the total number of deliverables for this proposal."""
        return self.deliverables.count()