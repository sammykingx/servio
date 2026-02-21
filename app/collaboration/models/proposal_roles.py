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
        
