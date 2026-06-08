from django.conf import settings
from django.db import models

from uuid6 import uuid7
from decimal import Decimal, ROUND_HALF_UP
from constants import SERVICE_FEE, GST_TAX_FEE, DECIMAL_PLACE, USD_TO_NGN_RATE, SUBSRIBERS_SERVICE_FEE
import urllib

class ContractStatus(models.TextChoices):
    AWAITING = "awaiting", "Awaiting Signatures"
    PENDING_ACTIVATION = "pending_activation", "Pending Activation"  # client signed + paid, awaiting provider
    SIGNED = "signed", "Signed" # both signed, not yet paid
    ACTIVATED = "activated", "Activated" # paid + both signed
    FUNDED = "funded", "Funded"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    DISPUTED = "disputed", "Disputed"


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
    
    client_accepted_terms_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp when the client accpeted the terms of the role contract but has not yet paid for the contract"
    )
    client_paid_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp when the client paid for the contract"
    )
    
    provider_accepted_terms_at = models.DateTimeField(null=True, blank=True)
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the contract was fully executed by both parties and marked as completed",
    )
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
            models.Index(fields=["slug"]),
            models.Index(fields=["reference"]),
        ]
        
        constraints = [
            models.CheckConstraint(
                name="check_contract_signed_requirements",
                condition=(
                    ~models.Q(status=ContractStatus.SIGNED) | 
                    (
                        models.Q(client_accepted_terms_at__isnull=False) & 
                        models.Q(provider_accepted_terms_at__isnull=False)
                    )
                )
            ),
        ]
        
    @property
    def is_fully_signed(self) -> bool:
        """Checks if both the client and provider have executed the contract."""
        return bool(self.client_paid_at and self.provider_accepted_terms_at)

    @property
    def has_client_accepted_terms(self) -> bool:
        """Helper checking only client timestamp presence."""
        return bool(self.client_accepted_terms_at)

    @property
    def has_provider_accepted_terms(self) -> bool:
        """Helper checking only provider timestamp presence."""
        return bool(self.provider_accepted_terms_at)

    @property
    def service_fee(self):
        """
        Calculates the fee dynamically by delegating the math directly 
        to the client's profile system.
        """
        return self.client.profile.calculate_service_fee(self.agreed_amount)

    @property
    def service_fee_to_ngn(self):
        """Calculates the service fee converted to NGN by delegating to the client's profile system."""
        return self.client.profile.service_fee_to_ngn(self.agreed_amount)
    
    @property   
    def tax(self):
        """Calculates the tax for the service based on the users region laws"""
        # outsoure the tax calculation to the users profile
        # to get the tax based on the users region and region taxing percent
        # return (
        #     self.agreed_amount * Decimal(str(GST_TAX_FEE))
        # ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
        pass

    @property
    def amount_payable(self):
        """The amount the client pays to kickstart the project, inclusive of service fee and tax"""
        return (
            self.agreed_amount + self.service_fee #+ self.tax
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
    
    @property
    def client_whatsapp_msg(self):
        project_title = self.project.title.title()
        number = self.client.profile.mobile_num
        message = (
                f"Hi {self.client.first_name.title()},\n\n"
                f"I'm reaching out regarding our project *\"{project_title}\"* on *Servio*.\n\n"
                "Everything looks good on my end regarding the deliverables and payment terms, "
                "and I'm ready to get started.\n\n"
                "Happy to coordinate here for updates and next steps.\n\n"
                "_— sent via *Servio* by DivGM_"
            )
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{number}?text={encoded_message}"
    
    @property
    def client_mail_msg(self):
        project_title = self.project.title.title()
        subject = f"Project Kickoff: {project_title} (via Servio)"
        email = self.client.email
        
        body = f"""
            Hi {self.client.first_name.title()},

            I hope you're doing well.

            I'm reaching out regarding our confirmed collaboration on the project "{project_title}" via Servio.

            Everything looks good on my end regarding the agreed scope and payment terms for my role, and I'm ready to get started.

            Please let me know the next steps or any initial direction you'd like me to follow.

            Happy to coordinate here or via WhatsApp for updates and communication.

            Looking forward to working with you.

            Best regards,  
            {self.provider.full_name.title()}

            —
            Sent via Servio by DivGM
            """

        encoded_subject = urllib.parse.quote(subject.strip())
        encoded_body = urllib.parse.quote(body.strip())

        return f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
        
    @property
    def provider_whatsapp_msg(self):
        number = self.provider.profile.mobile_num
        project_title = self.project.title.title()
        message = (
           f"Hi {self.provider.first_name.title()},\n\n"
           f"I'm reaching out regarding our project *\"{project_title}\"* on *Servio*.\n\n"
           "We've aligned on the deliverables and payment structure, and I'm looking forward "
           "to getting started with you.\n\n"
           "Feel free to use this chat for updates, coordination, and any questions along the way.\n\n"
           "_— sent via *Servio* by DivGM_"
        )
        
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{number}?text={encoded_message}"
    
    @property
    def provider_mail_msg(self):
        project_title = self.project.title.title()
        subject = f"Project Kickoff: {project_title} (via Servio)"
        email = self.provider.email
        
        body = f"""
            Hi {self.provider.first_name.title()},

            I hope you're doing well.

            I'm reaching out regarding our confirmed collaboration on the project "{project_title}" via Servio.

            Everything looks good on my end regarding the agreed scope and payment terms for my role, and I'm ready to get started.

            Please let me know the next steps or any initial direction you'd like me to follow.

            Happy to coordinate here or via WhatsApp for updates and communication.

            Looking forward to working with you.

            Best regards,  
            {self.client.full_name.title()}

            —
            Sent via Servio by DivGM
            """

        encoded_subject = urllib.parse.quote(subject.strip())
        encoded_body = urllib.parse.quote(body.strip())

        return f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
