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
    

def get_response_msg(action: GigStates, gig:GigPayload) -> CreateGigResponse:
    from core.url_names import CollaborationURLS
    from core.url_names import PaymentURLS
    
    responses = {
        GigStates.PUBLISH: CreateGigResponse(
            message="All set! Your gig/project is published, Hurray 🎉.",
            url=str(reverse_lazy(PaymentURLS.GIG_PAYMENT_SUMMARY, kwargs={"gig_id": gig.id},)),
        ),
        GigStates.DRAFT: CreateGigResponse(
            message="Your gig has been saved as a draft 📝, you can publish it later.",
            url=str(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS)),
            redirect=False,
        ),
    }

    return responses[action]
