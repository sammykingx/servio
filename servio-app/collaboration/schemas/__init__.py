from django.urls import reverse_lazy
from pydantic import BaseModel
from enum import Enum
from ..schemas.gig import GigPayload

class CreateGigStates(str, Enum):
    PUBLISH = "publish"
    DRAFT = "draft"
    
class CreateGigRequest(BaseModel):
    action: CreateGigStates
    payload: GigPayload
    
class CreateGigResponse(BaseModel):
    message: str
    redirect: bool = True
    url: str
    

def get_response_msg(action: CreateGigStates, gig:GigPayload) -> CreateGigResponse:
    from core.url_names import CollaborationURLS
    from core.url_names import PaymentURLS
    
    responses = {
        CreateGigStates.PUBLISH: CreateGigResponse(
            message="All set! Your gig/project is published 🎉, next step is payment.",
            url=str(reverse_lazy(PaymentURLS.GIG_PAYMENT_SUMMARY, kwargs={"gig_id": gig.id},)),
        ),
        CreateGigStates.DRAFT: CreateGigResponse(
            message="Your gig has been saved as a draft 📝, you can publish it later.",
            url=str(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS)),
            redirect=False,
        ),
    }

    return responses[action]
