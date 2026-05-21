from collaboration.models.choices import PaymentOption
from ...domain.constants import DurationUnit
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Union
from uuid import UUID

    
class ProposalDeliverable(BaseModel):
    """
    Represents a specific task or milestone within a proposed role.
    Handles the sequencing, duration constraints, and financial weight 
    of a single deliverable.
    """
    phase: str = Field(..., max_length=70)
    description: str = Field(..., max_length=2000)
    duration_unit: DurationUnit
    duration_value: int
    release_percentage: float = Field(..., ge=10.0, le=100.0)
    rendering_order: int = Field(..., description="The sequence position for UI rendering")

    @field_validator("description", mode="after")
    def validate_description(cls, value: str) -> str:
        return value.strip()
    
    @model_validator(mode='after')
    def validate_duration_logic(self) -> 'ProposalDeliverable':
        unit = self.duration_unit
        value = self.duration_value

        limits = {
            DurationUnit.DAYS: (1, 11),
            DurationUnit.WEEKS: (1, 4),
            DurationUnit.MONTHS: (1, 12),
        }

        min_val, max_val = limits[unit]

        if not (min_val <= value <= max_val):
            raise ValueError(
                f"For unit '{unit}', value must be between {min_val} and {max_val}. "
                f"Received: {value}"
            )

        return self

class ProposedRole(BaseModel):
    """
    Represents a specific service category (Industry/Niche) the provider 
    is applying for within the project.
    """
    industry_id: int = Field(..., description="Top-level service category ID")
    niche_id: int = Field(..., description="Specific skill/expertise level ID")
    niche_name: str = Field(..., description="Human-readable name of the expertise")
    role_amount: Union[Decimal, None] = None
    proposed_amount: Decimal = Field(..., gt=10, max_digits=12, decimal_places=2)
    currency: Literal["USD"] = "USD"
    payment_plan: PaymentOption = PaymentOption.SPLIT_50_50
    deliverables: List[ProposalDeliverable] = Field(..., min_length=1)
    
    @model_validator(mode='after')
    def validate_total_release_percentage(self) -> 'ProposedRole':
        total_percentage = sum(deliverable.release_percentage for deliverable in self.deliverables)
        
        if total_percentage != 100.0:
            raise ValueError(
                f"The total release percentage for all deliverables must equal 100%. "
                f"Current total is {total_percentage}%."
            )
            
        return self
    
    
class ProposalSubmissionPayload(BaseModel):
    """
    The root object for a proposal submission. 
    Links the provider's applied roles and financial terms to a specific project.
    """
    model_config = ConfigDict(strict=True)
    
    project_id: UUID
    applied_roles: List[ProposedRole] = Field(..., min_length=1)
    total_value: Decimal = Field(..., gt=5, max_digits=12, decimal_places=2)
    currency: Literal["USD"] = "USD"
    sent_at: datetime
    