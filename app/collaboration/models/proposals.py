from django.db import models
from django.conf import settings
from uuid6 import uuid7
from .choices import ProposalStatus



class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    gig = models.ForeignKey(
        "collaboration.Gig",
        on_delete=models.PROTECT,
        related_name="proposals",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="proposals",
    )

    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.SENT,
    )

    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "The worth of the user's proposal (summation of role amounts). "
            "This is filled after the proposal has been accepted."
        )
    )

    sent_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "proposal"
        verbose_name = "Project Proposal"
        verbose_name_plural = "Project Proposals"
        ordering = ["-created_at"]
        unique_together = ("gig", "user")
        indexes = [
            models.Index(fields=['user', 'status'], name='proposal_user_status_idx'),
            models.Index(fields=['gig', 'status'], name='proposal_gig_status_idx'),
            models.Index(fields=['user', 'gig'], name='proposal_user_gig_idx'),
        ]