from django.conf import settings
from django.db import models
from uuid6 import uuid7


class ContractStatus(models.TextChoices):
    AWAITING = "awaiting", "awaiting"
    SIGNED = "signed", "Signed"
    DECLINED = "declined", "Declined"

class Contract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    reference = models.CharField(max_length=35, unique=True)
    slug = models.SlugField(
        max_length=150,
        unique=True,
        editable=False,
        db_index=True
    )
    proposal = models.ForeignKey(
        "proposals.Proposal",
        on_delete=models.PROTECT,
        related_name="contracts",
    )
    proposal_role = models.OneToOneField(
        "proposals.ProposalRole",
        on_delete=models.PROTECT,
        related_name="contract",
    )
    project = models.ForeignKey(
        "collaboration.Gig",
        on_delete=models.PROTECT,
        related_name="contracts",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="client_contracts",
        to_field="email",
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="provider_contracts",
        to_field="email",
    )
    agreed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    payment_plan = models.CharField(max_length=40)

    status = models.CharField(
        max_length=30,
        choices=ContractStatus.choices,
        default=ContractStatus.AWAITING,
    )

    signed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "contracts"
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["provider", "status"]),
        ]
