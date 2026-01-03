from collaboration.models.choices import WorkMode
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


WORKMODE_OPTIONS = [
    {"value": WorkMode.FIXED_HOURS, "label":WorkMode.FIXED_HOURS.label},
    {"value": WorkMode.FLEXIBLE, "label": WorkMode.FLEXIBLE.label},
]


class WorkModeEnum(str, Enum):
    FIXED_HOURS = "fixed_hours"
    FLEXIBLE = "flexible"


class GigRolePayload(BaseModel):
    nicheId: int = Field(..., gt=1)
    niche: str
    professionalId: int = Field(..., gt=1)
    professional: str = Field(..., max_length=90)
    budget: Decimal = Field(..., gt=30)
    workload: WorkModeEnum = WorkMode.FLEXIBLE
    description: str = Field(..., max_length=330)
