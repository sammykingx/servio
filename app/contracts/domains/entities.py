from dataclasses import dataclass
from django.db.models import Model
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
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
        """Marks the contract as signed by the provider and updates status if client has also signed."""
        self.provider_accepted_terms_at = timezone.now()
        if self.client_accepted_terms_at:
            self.status = ContractStatus.SIGNED
            self.completed_at = timezone.now()
            
    def client_accepted_terms(self):
        """Marks the contract as signed by the client and updates status if provider has also signed."""
        self.client_accepted_terms_at = timezone.now()
        if self.provider_accepted_terms_at:
            self.status = ContractStatus.SIGNED
            self.completed_at = timezone.now()
    