from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class InitializePaymentPayload(BaseModel):
    reference: str
    provider: str
    
class PaystackInitializeAPIResponse(BaseModel):
    status: bool
    title: str
    message: str
    response_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    
#   "status": true,
#   "message": "Authorization URL created",
#   "data": {
#     "authorization_url": "https://checkout.paystack.com/3ni8kdavz62431k",
#     "access_code": "3ni8kdavz62431k",
#     "reference": "re4lyvq3s3"
#   }

# no access code
# gateway took too long
