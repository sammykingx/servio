from collaboration.models.choices import WorkMode
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from enum import Enum


WORKMODE_OPTIONS = [
    {"value": WorkMode.FIXED_HOURS, "label":WorkMode.FIXED_HOURS.label},
    {"value": WorkMode.FLEXIBLE, "label": WorkMode.FLEXIBLE.label},
]


class WorkModeEnum(str, Enum):
    FIXED_HOURS = "fixed_hours"
    FLEXIBLE = "flexible"


class GigRolePayload(BaseModel):
    nicheId: int = Field(..., gt=0)
    niche: str
    professionalId: int = Field(..., gt=0)
    professional: str = Field(..., max_length=90)
    budget: Decimal = Field(..., gt=30)
    workload: WorkModeEnum = WorkMode.FLEXIBLE
    description: str = Field(..., max_length=730)
    slots: Optional[int] = Field(1, gt=0)

