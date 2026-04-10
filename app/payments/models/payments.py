from django.conf  import settings
from django.db import models
from payments.domain.enums import RegisteredPaymentProvider, PaymentStatus, PaymentType
from uuid6 import uuid7


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field="email", related_name="payments", on_delete=models.CASCADE)
    reference = models.CharField(max_length=35, unique=True)
    gateway_reference = models.CharField(max_length=100, null=True, blank=True)
    idempotency_key = models.CharField(max_length=35, unique=True)
    amount = models.BigIntegerField()
    currency = models.CharField(max_length=10)
    type = models.CharField(max_length=20, choices=PaymentType.choices())
    status = models.CharField(max_length=20, choices=PaymentStatus.choices(), default=PaymentStatus.INITIATED)
    status_reason = models.CharField(max_length=255, null=True, blank=True)
    gateway = models.CharField(max_length=50, choices=RegisteredPaymentProvider.choices())
    is_processed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    @property
    def get_gateway(self):
        return RegisteredPaymentProvider(self.gateway)