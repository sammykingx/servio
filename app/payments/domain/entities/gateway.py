# Domain entities to represent gateway initialization and response for allregisterd gateways.

from dataclasses import dataclass, field
from payments.domain.enums import RegisteredPaymentProvider
from payments.schemas.paystack import PaystackInitData, PaystackVerificationData
from payments.schemas.stripe import StripeInitializationData, StripeVerificationData
from typing import Any, Dict, Union


@dataclass(frozen=True)
class GatewayInitResponse:
    """
    Normalized response from a payment gateway.

    Attributes:
        gateway (Union[RegisteredPaymentProvider, str]): The provider that handled the request.
        message (str): Status message returned by the gateway.
        data (Union[PaystackInitData, StripeInitializationData]): The actual payload/metadata from the gateway response.
    """
    gateway: Union[RegisteredPaymentProvider, str]
    message: str
    data: Union[
        PaystackInitData, 
        StripeInitializationData,
    ] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.gateway or not self.data:
            raise ValueError("Gateway result must include both a provider and response data.")
        
    def payload(self) -> Dict[str, Any]:
        """
        Standardizes the output for views/JSON responses.
        Ensures 'data' is always a raw dictionary.
        """
        normalized_data = self.data
        if hasattr(self.data, "model_dump"):
            normalized_data = self.data.model_dump()
        return {
            "gateway": self.gateway.value,
            "message": self.message,
            "data": normalized_data
        }
 
        
@dataclass(frozen=True)
class GatewayVerifyResponse:
    """
    Data transfer object representing the unified response from a payment gateway.

    This entity standardizes various provider responses into a consistent format 
    for the service layer to perform state transitions and integrity checks.

    Attributes:
        gateway (RegisteredPaymentProvider): The specific provider (e.g., Paystack) that processed the transaction.
        status (str): The status of the verification.
        message (str): The descriptive status message returned by the provider's API.
        was_successful (bool): Indicates if the transaction reached a terminal success state 
            on the gateway's end.
        data (Union[PaystackVerificationData, StripeVerificationData]): Raw, provider-specific payload containing granular transaction details 
            (e.g., amount in minor units, gateway/receipt id etc).
    """
    gateway: RegisteredPaymentProvider
    status: str
    message: str
    was_successful: bool
    data: Union[
        PaystackVerificationData, 
        StripeVerificationData,
    ] = field(default_factory=dict)
        