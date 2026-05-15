from dataclasses import dataclass
from django.contrib.auth.models import AbstractUser
from collaboration.models.choices import ProjectStatus, ProjectVisibility, PaymentOption
from datetime import datetime
from uuid import UUID
from decimal import Decimal


@dataclass
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
    
@dataclass
class RoleEntity:
    id: UUID
    project: ProjectEntity
    niche: int
    niche_name: str
    role_id: int
    role_name: str
    description: str
    budget: Decimal
    payment_plan: PaymentOption
    start_date: datetime
    end_date: datetime
    