from collaboration.models.choices import PaymentOption
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional


PAYMENT_OPTIONS = [
    {"value": member.value, "label": member.label}
    for member in PaymentOption
]


class GigRolePayload(BaseModel):
    nicheId: int = Field(..., gt=0)
    niche: str
    professionalId: int = Field(..., gt=0)
    professional: str = Field(..., max_length=90)
    budget: Decimal = Field(..., gt=30)
    paymentOption: PaymentOption = PaymentOption.SPLIT_50_50
    description: str = Field(..., max_length=730)
    slots: Optional[int] = Field(1, gt=0)

