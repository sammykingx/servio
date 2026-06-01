from django.conf  import settings
from django.db import models
from uuid6 import uuid7


class CanadaPayoutAccount(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field="email",
        related_name="canada_payout_accounts",
        on_delete=models.CASCADE
    )
    
    institution_number = models.CharField(max_length=25)
    transit_number = models.CharField(max_length=25)
    account_number = models.CharField(max_length=25)

    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = "canadian_payout_accounts"
        verbose_name = "Canadian Payout Account"
        verbose_name_plural = "Canadian Payout Accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "institution_number", "transit_number", "account_number"],
                name="unique_ca_account_per_user"
            )
        ]
    