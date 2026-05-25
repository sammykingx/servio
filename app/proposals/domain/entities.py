from dataclasses import dataclass, field
from django.contrib.auth.models import AbstractUser
from collaboration.models.choices import ProjectStatus, ProjectVisibility, PaymentOption
from proposals.models.choices import ProposalStatus, ProposalRoleStatus
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import List, Literal, TypeVar


ProposalRoleModelT = TypeVar("ProposalRole")
ProposalModelT = TypeVar("Proposal")


@dataclass(frozen=True) 
class ProjectRoleEntity:
    id: UUID
    niche: int
    niche_name: str
    role_id: int
    role_name: str
    description: str
    budget: Decimal
    payment_plan: PaymentOption
    status: str
    slots: int
    
    
@dataclass(frozen=True)
class ProjectEntity:
    id: UUID
    title: str
    description: str
    visibility: ProjectVisibility
    total_budget: Decimal
    is_gig_active: bool
    has_gig_roles: bool
    is_negotiable: bool
    creator: AbstractUser
    status: ProjectStatus
    start_date: datetime
    end_date: datetime
    required_roles: List[ProjectRoleEntity] = field(default_factory=list)

 
@dataclass
class ProposalEntity:
    id: UUID
    project: ProjectEntity
    provider: AbstractUser
    total_value: Decimal
    currency: str
    status: ProposalStatus
    sent_at: datetime
    created_at: datetime
    roles: List[ProjectRoleEntity]
    

@dataclass
class ProposalRoleEntity:
    id: UUID
    role_fk: UUID
    category_fk: int
    description: str
    client_budget: Decimal
    proposed_amount: Decimal
    currency: Literal["USD", "NGN"]
    payment_plan: PaymentOption
    status: ProposalRoleStatus

    # not used
    @classmethod
    def from_model(cls, model_instance: ProposalRoleModelT) -> "ProposalRoleEntity":
        """Factory method to create a domain entity from the proposal role model."""
        return cls(
            id=model_instance.id,
            role_fk=model_instance.role_id, 
            category_fk=model_instance.category_id,
            client_budget=model_instance.client_budget,
            proposed_amount=model_instance.proposed_amount,
            currency=model_instance.currency,
            payment_plan=model_instance.payment_plan,
            status=model_instance.status
        )
