from django.urls import reverse_lazy
from pydantic import BaseModel
from enum import Enum
from ..schemas.gig import GigPayload

class GigStates(str, Enum):
    PUBLISH = "publish"
    DRAFT = "draft"
    PENDING = "pending"
    
class CreateGigRequest(BaseModel):
    action: GigStates
    payload: GigPayload
    
class CreateGigResponse(BaseModel):
    message: str
    redirect: bool = True
    url: str
