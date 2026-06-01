from django.conf  import settings
from django.db import models
from uuid6 import uuid7


class USPayoutAccount(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid7)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field="email",
        related_name="us_payout_accounts",
        on_delete=models.CASCADE
    )
    
    routing_number = models.CharField(max_length=25)
    account_number = models.CharField(max_length=25)

    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = "us_payout_accounts"
        verbose_name = "US Payout Account"
        verbose_name_plural = "US Payout Accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "routing_number", "account_number"],
                name="unique_us_account_per_user"
            )
        ]