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
        related_name="proposal_roles",
        blank=True,
        null=True,
        help_text=(
            "Optional only if the parent Gig does not use structured roles. "
            "Must be provided for role-specific proposals to ensure contract integrity."
        ),
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
    
    class Meta:
        db_table = "proposal_roles"
        verbose_name = "Proposal Role"
        verbose_name_plural = "Proposal Roles"
        
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.proposal.gig.has_gig_roles and not self.gig_role:
            raise ValidationError("This project requires a specific gig_role selection to proceed with the proposal since the gig has roles attached.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
