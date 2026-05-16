from django.db import models
from collaboration.models.choices import PaymentOption
from .choices import ProposalRoleStatus
from constants import DECIMAL_PLACE, SERVICE_FEE
from decimal import Decimal, ROUND_HALF_UP


class ProposalRole(models.Model):
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
        help_text=(
            "Optional only if the parent Gig use structured roles. "
            "Must be provided for role-specific proposals to ensure contract integrity."
        ),
    )
    
    category = models.ForeignKey(
        "collaboration.GigCategory",
        on_delete=models.PROTECT,
        related_name="proposal_roles_by_category",
        blank=True,
        null=True,
        help_text="Link to a GigCategory if the gig does not have structured roles."
    )

    # amount = models.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    # )

    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=10)

    payment_plan = models.CharField(
        max_length=20,
        choices=PaymentOption.choices,
    )
    
    status = models.CharField(
        max_length=20,
        choices=ProposalRoleStatus.choices,
        default=ProposalRoleStatus.SUBMITTED,
    )
    
    class Meta:
        db_table = "proposal_roles"
        verbose_name = "Proposal Role"
        verbose_name_plural = "Proposal Roles"
        
    @property
    def role_name(self):
        """
        Returns the name of the role, whether it's from a GigRole or a GigCategory.
        This makes template rendering simple.
        """
        if self.role:
            return self.role.role_name
        elif self.category:
            return self.category.name
        return "Unknown Role"
    
    @property
    def dynamic_budget_range(self):
        amount = self.proposed_amount
        lower_raw = amount * Decimal('0.6')
        upper_raw = amount * Decimal('1.1')

        lower = (lower_raw / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10
        upper = (upper_raw / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10

        min_limit = Decimal('50')
        display_lower = max(lower, min_limit)

        return f"${display_lower:,.0f} - ${upper:,.0f}"
    
    # @property
    # def budget_difference(self):
    #     diff = self.proposed_amount - self.role_amount
    #     return f"+${diff:,.2f}" if diff > 0 else f"-${abs(diff):,.2f}" if diff < 0 else "No Change"
    
    # @property
    # def service_fee(self):
    #     return (
    #         self.final_amount * Decimal(str(SERVICE_FEE))
    #     ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
    
    # @property
    # def payout_amount(self):
    #     return (
    #         self.final_amount - self.service_fee
    #     ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
        
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.role and self.category:
            raise ValidationError("A ProposalRole can only have either a role or a category, not both.")
        if not self.role and not self.category:
            raise ValidationError("A ProposalRole must have either a role or a category, not both.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
