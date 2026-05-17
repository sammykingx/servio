from dataclasses import dataclass, field
from django.contrib.auth.models import AbstractUser
from collaboration.models.choices import ProjectStatus, ProjectVisibility, PaymentOption
from proposals.models.choices import ProposalStatus, ProposalRoleStatus
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import List, Literal


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
   

class ProposalEntity:
    id: UUID
    project: ProjectEntity
    provider: AbstractUser
    total_value: Decimal
    currency: str
    status: ProposalStatus
    sent_at: datetime
    created_at: datetime


class ProposalRoleEntity:
    id: UUID
    project_role: UUID
    client_budget: Decimal
    proposed_amount: Decimal
    currency: Literal["USD", "NGN"]
    payment_plan: PaymentOption
    status: ProposalRoleStatus
    
    def accept(self) -> None:
        """Transitions the role state to ACCEPTED if valid."""
        # if self.status == ProposalRoleStatus.REJECTED:
            # raise DomainValidationError("Cannot accept a previously rejected proposal role.")
        self.status = ProposalRoleStatus.ACCEPTED

    def reject(self) -> None:
        """Transitions the role state to REJECTED."""
        self.status = ProposalRoleStatus.REJECTED