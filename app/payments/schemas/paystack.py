from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Any, Dict

class PaystackInitializationData(BaseModel):
    """The actual payload containing checkout details."""
    authorization_url: HttpUrl
    access_code: str
    reference: str

class PaystackInitializationResponseSchema(BaseModel):
    """The full API response structure from Paystack initialization API."""
    message: str
    data: PaystackInitializationData
    
# {
#   "status": True,
#   "message": "Authorization URL created",
#   "data": {
#     "authorization_url": "https://checkout.paystack.com/3ni8kdavz62431k",
#     "access_code": "3ni8kdavz62431k",
#     "reference": "re4lyvq3s3"
#   }
# }


class PaystackVerificationResponseData(BaseModel):
    id: int
    reference: str
    gateway_response: str
    amount:  int
    paid_at: datetime


class PaystackVerificationResponseSchema(BaseModel):
    message: str
    data: PaystackVerificationResponseData
    metadata: Dict[str, Any] = Field(default_factory=dict)