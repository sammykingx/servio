from django.conf  import settings
from django.db import models
from payments.domain.enums import RegisteredPaymentProvider, PaymentStatus, PaymentType, PaymentPurpose
from uuid6 import uuid7


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field="email", related_name="payments", on_delete=models.CASCADE)
    reference = models.CharField(max_length=35, unique=True)
    gateway_reference = models.CharField(max_length=100, null=True, blank=True)
    amount_decimal = models.DecimalField(max_digits=12, decimal_places=2)
    amount_in_minor_units = models.BigIntegerField()
    currency = models.CharField(max_length=10)
    payment_type = models.CharField(max_length=30, choices=PaymentType.choices())
    payment_purpose = models.CharField(max_length=30, choices=PaymentPurpose.choices())
    status = models.CharField(max_length=20, choices=PaymentStatus.choices(), default=PaymentStatus.INITIATED)
    gateway = models.CharField(max_length=20, choices=RegisteredPaymentProvider.choices())
    gateway_response = models.CharField(max_length=100, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "payments_ledger"
        verbose_name = "Payment Ledger"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "payment_purpose"],
                condition=models.Q(status="success"),
                name="unique_successful_activation_per_user"
            )
        ]
        
        indexes = [
            # Fast activation payment lookup
            models.Index(
                fields=["user", "payment_purpose", "status"],
                name="idx_user_purpose_status"
            ),

            # Webhook processing safety
            models.Index(
                fields=["reference", "is_processed"],
                name="idx_ref_processed"
            ),

            # Dashboard / analytics queries
            models.Index(
                fields=["status"],
                name="idx_status"
            ),

            # Gateway-based filtering (useful later)
            models.Index(
                fields=["gateway", "status"],
                name="idx_gateway_status"
            ),

            # Sorting recent payments fast
            models.Index(
                fields=["-created_at"],
                name="idx_created_desc"
            ),
        ]
    
    @property
    def get_gateway(self):
        return RegisteredPaymentProvider(self.gateway)