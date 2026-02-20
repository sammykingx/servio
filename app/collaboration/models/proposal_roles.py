from django.db import models
from django.conf import settings
from uuid6 import uuid7
from .choices import PaymentOption, ProposalStatus


class ProposalRole(models.Model):
    proposal = models.ForeignKey(
        "collaboration.Proposal",
        on_delete=models.CASCADE,
        related_name="roles",
    )

    gig_role = models.ForeignKey(
        "collaboration.GigRole",
        on_delete=models.PROTECT,
        related_name="proposal_roles",
    )

    role_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    payment_plan = models.CharField(
        max_length=20,
        choices=PaymentOption.choices,
    )    
    

class GigNegotiation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    application = models.ForeignKey(
        "collaboration.GigApplication",
        on_delete=models.CASCADE,
        related_name="negotiations"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_negotiations"
    )

    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
