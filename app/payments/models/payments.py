from django.conf  import settings
from django.db import models
from payments.domain.enums import RegisteredPaymentProvider, PaymentStatus, PaymentType, PaymentPurpose
from uuid6 import uuid7
from constants import APP_NAME


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field="email", related_name="payments", on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        to_field="email", 
        related_name="earnings", 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    reference = models.CharField(max_length=35, unique=True)
    gateway_reference = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="The unique tracking string (e.g., Paystack access_code or Stripe Client Secret) used to identify the transaction attempt."
    )
    gateway_order_id = models.PositiveBigIntegerField(
        null=True, 
        blank=True, 
        unique=True,
        help_text="To identify the success.",
    )
    amount_decimal = models.DecimalField(max_digits=12, decimal_places=2)
    amount_in_minor_units = models.BigIntegerField()
    paid_amount_in_minor = models.BigIntegerField(blank=True, null=True)
    currency = models.CharField(max_length=10)
    payment_type = models.CharField(max_length=30, choices=PaymentType.choices())
    payment_purpose = models.CharField(max_length=30, choices=PaymentPurpose.choices())
    status = models.CharField(max_length=20, choices=PaymentStatus.choices(), default=PaymentStatus.INITIATED)
    gateway = models.CharField(max_length=20, choices=RegisteredPaymentProvider.choices())
    gateway_response = models.CharField(max_length=200, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user": self.user.email if self.user else None,
            "reference": self.reference,
            "beneficiary": self.beneficiary,
            "gateway_reference": self.gateway_reference,
            "amount_decimal": str(self.amount_decimal),
            "amount_in_minor_units": self.amount_in_minor_units,
            "currency": self.currency,
            "payment_type": self.payment_type,
            "payment_purpose": self.payment_purpose,
            "status": self.status,
            "gateway": self.gateway,
            "gateway_response": self.gateway_response,
            "is_processed": self.is_processed,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    class Meta:
        db_table = "payments_ledger"
        verbose_name = "Payment Ledger"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "payment_purpose", "reference"],
                condition=models.Q(status="success"),
                name="unique_successful_transaction_per_user"
            )
        ]
        
        indexes = [
            models.Index(
                fields=["user", "payment_type", "payment_purpose", "status"],
                name="idx_user_purpose_status"
            ),
            
            models.Index(
                fields=["reference"],
                name="idx_payment_reference",
            ),
            
            models.Index(
                fields=["user", "reference"],
                name="idx_user_payment_reference",
            ),

            # Webhook processing safety
            models.Index(
                fields=["reference", "is_processed"],
                name="idx_ref_processed"
            ),

            # Dashboard / analytics queries
            # models.Index(
            #     fields=["status"],
            #     name="idx_status"
            # ),

            # Gateway-based filtering (useful later)
            # models.Index(
            #     fields=["gateway", "status"],
            #     name="idx_gateway_status"
            # ),

            # Sorting recent completed payments by status fast
            models.Index(
                fields=["status", "-paid_at"],
                name="idx_completed_payment_desc"
            ),
        ]
    
    @property
    def display_recipient_name(self):
        if self.payment_purpose == PaymentPurpose.ACTIVATION_FEE:
            return f"{APP_NAME.title()} Platform"
        return self.user.full_name or self.user.email
    