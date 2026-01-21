from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from typing import List
from decimal import Decimal
from enum import Enum
from .gig_role import GigRolePayload
import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "b", "em", "i", "u",
    "ul", "ol", "li",
    "h1", "h2", "h3", "h4",
    "blockquote",
    "span",
    "div"
]

ALLOWED_ATTRIBUTES = {
    "*": ["class", "style"],
}

ALLOWED_STYLES = [
    "text-align",
    "font-weight",
    "font-style",
    "text-decoration",
]

class VisibilityEnum(str, Enum):
    public = "public"
    private = "private"

class GigPayload(BaseModel):
    title: str = Field(..., max_length=320)
    description: str = Field(..., max_length=3000)
    projectBudget: Decimal = Field(..., gt=0)
    visibility: VisibilityEnum
    startDate: date
    endDate: date
    isNegotiable: bool
    roles: List[GigRolePayload] = Field(default_factory=list)
    

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value: str):
        # value = bleach.clean(
        #     value,
        #     tags=ALLOWED_TAGS,
        #     attributes=ALLOWED_ATTRIBUTES,
        #     strip=True
        # )
        return value
    
    @field_validator("startDate", mode="after")
    @classmethod
    def validate_start_date(cls, value: date):
        if value < date.today():
            raise ValueError("startDate cannot be in the past")
        return value
    
    @model_validator(mode='after')
    def validate_date_range(self):
        if self.endDate <= self.startDate:
            raise ValueError("endDate must be greater than startDate")
        return self
    
    @model_validator(mode="after")
    def validate_roles_budget(self):
        total_roles_budget = sum(role.budget for role in self.roles)
        if total_roles_budget > self.projectBudget:
            raise ValueError("Sum of role budgets exceeds projectBudget")
        return self
