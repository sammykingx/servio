from ..models.choices import PaymentOption
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Union


class DurationUnit(str, Enum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    
class DeliverablesPayload(BaseModel):
    description: str = Field(..., max_length=2000)
    duration_unit: DurationUnit
    duration_value: int
    due_date: date

    @field_validator("description", mode="after")
    def validate_description(cls, value) -> str:
        return value.strip()
    
    @model_validator(mode='after')
    def validate_duration_logic(self) -> 'DeliverablesPayload':
        unit = self.duration_unit
        value = self.duration_value

        limits = {
            DurationUnit.DAYS: (1, 6),
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

class AppliedRoles(BaseModel):
    industry_id: int 
    niche_id: int
    role_amount: Decimal = Field(..., gt=0)
    proposed_amount: Union[Decimal, None] = None
    payment_plan: PaymentOption = PaymentOption.SPLIT_50_50
    
    
class SendProposal(BaseModel):
    applied_roles: List[AppliedRoles]
    deliverables: List[DeliverablesPayload]
    proposal_value: Decimal = Field(..., gt=0)
    sent_at: datetime