from dataclasses import dataclass
from django.db.models import Model
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from contracts.domains.errors import ContractPolicyFailure
from contracts.domains.exceptions import ContractException
from contracts.models.contract import ContractStatus
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Literal

@dataclass(frozen=True)
class ContractGenerationContext:
    """
    An immutable DTO representing the verified context handed off 
    from the Proposal service to the Contract service.
    """
    proposal: Model
    accepted_role: Model


@dataclass
class ContractEntity:
    """
    A domain entity representing the core attributes and behaviors of a contract
    within the system. This class serves as a blueprint for contract-related
    operations and encapsulates any business logic directly tied to the contract's lifecycle.
    """
    id: UUID
    reference: str
    slug: str
    proposal_id: UUID
    proposal_role_id: UUID
    project_id: UUID
    client: AbstractUser
    provider: AbstractUser
    agreed_amount: Decimal
    currency: Literal["USD", "NGN"]
    payment_plan: str
    status: ContractStatus
    client_paid_at: datetime
    client_accepted_terms_at: datetime
    provider_accepted_terms_at: datetime
    completed_at: datetime
    
    
    @classmethod
    def from_model(cls, instance: Model) -> "ContractEntity":
        """
        Factory method to instantiate a clean Domain Entity from a 
        Django ORM Contract model instance.
        """
        return cls(
            id=instance.id,
            reference=instance.reference,
            slug=instance.slug,
            proposal_id=instance.proposal_id,
            proposal_role_id=instance.proposal_role_id,
            project_id=instance.project_id,
            client=instance.client,
            provider=instance.provider,
            agreed_amount=instance.agreed_amount,
            currency=instance.currency,
            payment_plan=instance.payment_plan,
            status=instance.status,
            client_accepted_terms_at=instance.client_accepted_terms_at,
            client_paid_at=instance.client_paid_at,
            provider_accepted_terms_at=instance.provider_accepted_terms_at,
            completed_at=instance.completed_at,
            
        )
    
    def provider_accepted_terms(self):
        """
        Provider accepts terms.
        If client has already paid, contract moves to ACTIVATED immediately.
        If client has signed but not paid, contract moves to SIGNED.
        If client hasn't signed at all, status stays AWAITING.
        """
        if self.provider_accepted_terms_at:
            return
        self.provider_accepted_terms_at = timezone.now()
        
        if self.client_paid_at:
            self.status = ContractStatus.ACTIVATED
        elif self.client_accepted_terms_at:
            self.status = ContractStatus.SIGNED
            
    def client_accepted_terms(self):
        """
        Client accepts terms. Does not change status to SIGNED because
        the provider may not have signed yet. Client proceeds to pay from
        this state regardless of provider signature status.
        """
        if self.client_accepted_terms_at:
            return
        self.client_accepted_terms_at = timezone.now()
        
    def client_paid(self):
        """
        Client completes activation payment.
        If provider has already signed, contract is fully ACTIVATED.
        If provider hasn't signed yet, contract moves to PENDING_ACTIVATION
        to await the provider's signature.
        """
        if not self.client_accepted_terms_at:
            raise ContractException(
                "Client must accept contract terms before contract activiation.",
                code=ContractPolicyFailure.TERMS_NOT_ACKNOWLEDGED.code,
                title=ContractPolicyFailure.TERMS_NOT_ACKNOWLEDGED.title,
            )
        
        self.client_paid_at = timezone.now()
        
        if self.provider_accepted_terms_at:
            self.status = ContractStatus.ACTIVATED
        else:
            self.status = ContractStatus.PENDING_ACTIVATION
    