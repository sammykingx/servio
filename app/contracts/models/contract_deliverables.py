from django.conf import settings
from django.db import models

# not used
class ContractDeliverable(models.Model):
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="deliverables",
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="contract_deliverables",
        on_delete=models.CASCADE,
        to_field="email",
    )
    phase = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    release_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of contract agreed_amount released when this deliverable is approved."
    )
    release_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Computed at contract creation: agreed_amount × (release_percentage / 100). Stored so it never drifts if amounts are ever adjusted."
    )
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Defines the display sequence to preserve the order in which deliverables were entered.",
    )
    
    class Meta:
        db_table="contract_deliverables"
        ordering = ["order", "pk"]
        verbose_name = "Contract Deliverable"
        verbose_name_plural = "Contract Deliverables"