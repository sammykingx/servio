from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Any, Dict, Union

class PaystackInitData(BaseModel):
    """The actual payload containing checkout details."""
    authorization_url: HttpUrl
    access_code: str
    reference: str

class PaystackInitResponseSchema(BaseModel):
    """The full API response structure from Paystack initialization API."""
    message: str
    data: PaystackInitData

class PaystackVerificationData(BaseModel):
    id: int
    status: str
    amount:  int
    paid_at: Union[datetime, None]
    paystack_metadata: Dict[str, Any] = Field(default_factory=dict)
