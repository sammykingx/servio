from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from typing import List
from decimal import Decimal
from enum import Enum
from .gig_role import GigRolePayload
import bleach, html


ALLOWED_TAGS = [
    "p", "br", "strong", "b", "em", "i", "u",
    "ul", "ol", "li",
    "h1", "h2", "h3", "h4",
    "blockquote",
    "span",
    "div"
]


class VisibilityEnum(str, Enum):
    public = "public"
    private = "private"

class GigPayload(BaseModel):
    """Editting gig that is in draft mode"""
    
    title: str = Field(..., max_length=120)
    description: str
    projectBudget: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    visibility: VisibilityEnum
    startDate: date
    endDate: date
    isNegotiable: bool
    roles: List[GigRolePayload] = Field(default_factory=list)

    @field_validator("description", mode="before")
    @classmethod
    def clean_description(cls, value: str):
        plain = bleach.clean(value, tags=ALLOWED_TAGS, strip=True)
        sanitized = bleach.clean(plain, tags=[], strip=True).strip()
        
        if len(sanitized) > 2000:
            raise ValueError("Project description is too long, reduce the length to provide a better experience for professionals browsing through projects.")
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
