from django.conf import settings
from django.db import models
from uuid6 import uuid7
from decimal import Decimal, ROUND_HALF_UP
from constants import SERVICE_FEE, GST_TAX_FEE, DECIMAL_PLACE


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

    client_signed_at = models.DateTimeField(null=True, blank=True)
    provider_signed_at = models.DateTimeField(null=True, blank=True)
    
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
        
    property
    def is_fully_signed(self) -> bool:
        """Checks if both the client and provider have executed the contract."""
        return bool(self.client_signed_at and self.provider_signed_at)

    @property
    def has_client_signed(self) -> bool:
        """Helper checking only client timestamp presence."""
        return bool(self.client_signed_at)

    @property
    def has_provider_signed(self) -> bool:
        """Helper checking only provider timestamp presence."""
        return bool(self.provider_signed_at)

    @property
    def service_fee(self):
        return (
            self.agreed_amount * Decimal(str(SERVICE_FEE))
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
    
    @property   
    def tax(self):
        return (
            self.agreed_amount * Decimal(str(GST_TAX_FEE))
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)

    @property
    def amount_payable(self):
        """The amount the client pays to kickstart the project, inclusive of service fee and tax"""
        return (
            self.agreed_amount + self.service_fee + self.tax
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
        
    @property
    def amount_receivable(self):
        """The amount the provider receives after deducting service fee"""
        return (
            self.agreed_amount - self.service_fee
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
        
    @property
    def payment_plan_display(self):
        return self.payment_plan.strip("split_").replace("_", "% , ").rstrip() + "%"
