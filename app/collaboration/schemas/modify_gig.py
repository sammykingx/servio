from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
from datetime import date
from typing import List


class ModifyLiveGigRoles(BaseModel):
    industry_id: int = Field(..., gt=0)
    role_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    
class MetaData(BaseModel):
    is_balanced: bool
    roles_sum: Decimal

class ModifyLiveGig(BaseModel):
    start_date: date
    end_date: date
    project_budget: Decimal = Field(..., ge=50, max_digits=12, decimal_places=2),
    roles: List[ModifyLiveGigRoles] = Field(default_factory=list)
    metadata: MetaData
    
    @field_validator("start_date", mode="after")
    @classmethod
    def validate_start_date(cls, value: date):
        if value < date.today():
            raise ValueError("commencement day cannot be in the past")
        return value
    
    @model_validator(mode='after')
    def validate_date_range(self):
        if self.end_date <= self.start_date:
            raise ValueError("Est. due date must be greater than commencement day")
        return self