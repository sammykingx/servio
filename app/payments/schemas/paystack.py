from pydantic import BaseModel, HttpUrl


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