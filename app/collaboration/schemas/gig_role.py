from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from enum import Enum


class PaymentModeEnum(str, Enum):
    FULL_UPFRONT = "full_upfront"
    
    SPLIT_50_50 = "split_50_50"
    SPLIT_60_40 = "split_60_40"
    SPLIT_70_30 = "split_70_30"
    
    SPLIT_30_40_30 = "split_30_40_30"
    SPLIT_40_30_30 = "split_40_30_30"
    SPLIT_50_30_20 = "split_50_30_20"

    @property
    def label(self) -> str:
        return {
            PaymentModeEnum.FULL_UPFRONT: "100% Upfront",
            PaymentModeEnum.SPLIT_50_50: "50% / 50%",
            PaymentModeEnum.SPLIT_60_40: "60% / 40%",
            PaymentModeEnum.SPLIT_70_30: "70% / 30%",
            PaymentModeEnum.SPLIT_30_40_30: "30% / 40% / 30%",
            PaymentModeEnum.SPLIT_40_30_30: "40% / 30% / 30%",
            PaymentModeEnum.SPLIT_50_30_20: "50% / 30% / 20%",
        }[self]


PAYMENT_OPTIONS = [
    {"value": mode.value, "label": mode.label}
    for mode in PaymentModeEnum
]


class GigRolePayload(BaseModel):
    nicheId: int = Field(..., gt=0)
    niche: str
    professionalId: int = Field(..., gt=0)
    professional: str = Field(..., max_length=90)
    budget: Decimal = Field(..., gt=30)
    paymentOption: PaymentModeEnum = PaymentModeEnum.SPLIT_50_50
    description: str = Field(..., max_length=730)
    slots: Optional[int] = Field(1, gt=0)

