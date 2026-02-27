from django.db import models
from .choices import PaymentOption


class ProposalRole(models.Model):
    proposal = models.ForeignKey(
        "collaboration.Proposal",
        on_delete=models.CASCADE,
        related_name="roles",
    )

    gig_role = models.ForeignKey(
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
    
    gig_category = models.ForeignKey(
        "collaboration.GigCategory",
        on_delete=models.PROTECT,
        related_name="proposal_roles_by_category",
        blank=True,
        null=True,
        help_text="Link to a GigCategory if the gig does not have structured roles."
    )

    role_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    payment_plan = models.CharField(
        max_length=20,
        choices=PaymentOption.choices,
    )
    # has_gig_role = models.BooleanField()   
    
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
        if self.gig_role:
            return self.gig_role.role_name
        elif self.gig_category:
            return self.gig_category.name
        return "Unknown Role"
        
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.gig_role and self.gig_category:
            raise ValidationError("A ProposalRole can only have either a gig_role or a gig_category, not both.")
        if not self.gig_role and not self.gig_category:
            raise ValidationError("A ProposalRole must have either a gig_role or a gig_category,not both.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
