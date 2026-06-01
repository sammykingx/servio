from core.model_registry import registry
from django.conf  import settings
from django.db import models
from uuid6 import uuid7


class PayoutDestination(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field="email",
        related_name="payout_destinations",
        on_delete=models.CASCADE
    )
    country = models.CharField(max_length=50)
    currency = models.CharField(max_length=10)
    linked_account_id = models.UUIDField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "payout_destinations"
        verbose_name = "Payout Destination"
        verbose_name_plural = "Payout Destinations"
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="unique_default_payout_per_user"
            )
        ]
        
    @classmethod
    def can_receive_payout(cls, user, currency=None) -> bool:
        return (
            cls.objects.filter(user=user).exists()
        )
    
    @classmethod
    def get_all(cls, user):
        return cls.objects.filter(user=user).order_by("-created_at")
  
    @classmethod
    def get_default(cls, user):
        return cls.objects.filter(user=user, is_default=True).first()
    
    @classmethod
    def get_fallback_for_payout(cls, user, currency=None):
        """
        Returns best payout destination:
        1. default account if exists
        2. otherwise match by currency
        3. otherwise None (hold payout)
        """

        default = cls.get_default(user)
        if default:
            return default

        if currency:
            match = (
                cls.objects
                .filter(user=user, currency=currency)
                .first()
            )
            if match:
                return match

        return None
    
    def resolve_account(self):
        if self.country == "CA":
            return registry.CanadaPayoutAccount.objects.get(id=self.linked_account_id)

        elif self.country == "US":
            return registry.USPayoutAccount.objects.get(id=self.linked_account_id)

        elif self.country == "NG":
            return registry.NigeriaPayoutAccount.objects.get(id=self.linked_account_id)

        return None