from pydantic import BaseModel, Field
from typing import Any, Dict


class StripeInitializationResponseSchema(BaseModel):
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    
class StripeInitializationData(BaseModel):
    pass

class StripeVerificationData(BaseModel):
    pass