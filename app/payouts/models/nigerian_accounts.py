from django.conf  import settings
from django.db import models
from uuid6 import uuid7

class NigeriaPayoutAccount(models.Model):
    id = models.UUIDField(default=uuid7, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field="email",
        related_name="nigeria_payout_accounts",
        on_delete=models.CASCADE
    )

    bank_code = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=70)
    account_number = models.CharField(max_length=15)
    account_name = models.CharField(max_length=50)

    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = "nigerian_payout_accounts"
        verbose_name = "Nigerian Payout Account"
        verbose_name_plural = "Nigerian Payout Accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "bank_code", "account_number"],
                name="unique_ng_account_per_user"
            )
        ]
    