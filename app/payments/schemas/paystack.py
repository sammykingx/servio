from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Any, Dict

class PaystackInitData(BaseModel):
    """The actual payload containing checkout details."""
    authorization_url: HttpUrl
    access_code: str
    reference: str

class PaystackInitResponseSchema(BaseModel):
    """The full API response structure from Paystack initialization API."""
    message: str
    data: PaystackInitData
    
# {
#   "status": True,
#   "message": "Authorization URL created",
#   "data": {
#     "authorization_url": "https://checkout.paystack.com/3ni8kdavz62431k",
#     "access_code": "3ni8kdavz62431k",
#     "reference": "re4lyvq3s3"
#   }
# }


class PaystackVerificationData(BaseModel):
    id: int
    status: str
    amount:  int
    paid_at: datetime
    paystack_metadata: Dict[str, Any] = Field(default_factory=dict)
