from django.db import models
from django.conf import settings


class DurationUnit(models.TextChoices):
    DAYS = "days", "Days"
    WEEKS = "weeks", "Weeks"
    MONTHS = "months", "Months"

class ProposalDeliverable(models.Model):
    proposal = models.ForeignKey(
        "collaboration.Proposal",
        on_delete=models.CASCADE,
        related_name="deliverables",
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field="email",
        related_name="proposal_deliverables",
    )

    # will be enabled when role based proposl is allowed
    # role = models.ForeignKey(
    #     "collaboration.ProposalRole",
    #     on_delete=models.CASCADE,
    #     related_name="deliverables",
    #     null=True,
    #     blank=True,
    # )
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=2010)

    duration_unit = models.CharField(
        max_length=20,
        choices=DurationUnit.choices,
    )

    duration_value = models.PositiveIntegerField()
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Defines the display sequence to preserve the order in which deliverables were entered.",
    )
    
    class Meta:
        db_table="deliverables"
        ordering = ["order", "pk"]
        verbose_name = "Proposal Deliverable"
        verbose_name_plural = "Proposal Deliverables"