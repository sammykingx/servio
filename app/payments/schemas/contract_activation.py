from pydantic import BaseModel
from payments.domain.enums import RegisteredPaymentProvider


class ContractActivationPayload(BaseModel):
    """Payload for initiating the contract activation payment process."""
    
    contract_reference: str
    gateway: RegisteredPaymentProvider