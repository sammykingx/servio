from django.db import models
from django.conf import settings
from .choices import DurationUnit


class ProposalDeliverable(models.Model):
    proposal_role = models.ForeignKey(
        "ProposalRole",
        on_delete=models.CASCADE,
        related_name="deliverables",
    )
    
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field="email",
        related_name="proposal_deliverables",
    )

    phase = models.CharField(max_length=60)
    description = models.TextField(max_length=2010)

    duration_unit = models.CharField(
        max_length=20,
        choices=DurationUnit.choices,
    )

    duration_value = models.PositiveIntegerField()
    rendering_order = models.PositiveIntegerField(
        default=0,
        help_text="Defines the display sequence to preserve the order in which deliverables were entered.",
    )
    release_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of agreed_amount released upon approval of this deliverable. All deliverables on a role must sum to 100."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table="deliverables"
        ordering = ["rendering_order", "pk"]
        verbose_name = "Proposal Deliverable"
        verbose_name_plural = "Proposal Deliverables"