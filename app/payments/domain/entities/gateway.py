# Domain entities to represent gateway initialization and response for allregisterd gateways.

from dataclasses import dataclass, field
from payments.domain.enums import RegisteredPaymentProvider
from payments.schemas.paystack import PaystackInitData, PaystackVerificationData
from payments.schemas.stripe import StripeInitializationData, StripeVerificationData
from typing import Union


@dataclass(frozen=True)
class GatewayInitResponse:
    """
    Normalized response from a payment gateway.

    Attributes:
        gateway: The provider that handled the request.
        message: Status message returned by the gateway.
        data: The actual payload/metadata from the gateway response.
    """
    gateway: RegisteredPaymentProvider
    message: str
    data: Union[
        PaystackInitData, 
        StripeInitializationData,
    ] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.gateway or not self.data:
            raise ValueError("Gateway result must include both a provider and response data.")
 
        
@dataclass(frozen=True)
class GatewayVerifyResponse:
    """
    Data transfer object representing the unified response from a payment gateway.

    This entity standardizes various provider responses into a consistent format 
    for the service layer to perform state transitions and integrity checks.

    Attributes:
        gateway: The specific provider (e.g., Paystack) that processed the transaction.
        message: The descriptive status message returned by the provider's API.
        is_successful: Indicates if the transaction reached a terminal success state 
            on the gateway's end.
        data: Raw, provider-specific payload containing granular transaction details 
            (e.g., amount in minor units, gateway/receipt id etc).
    """
    gateway: RegisteredPaymentProvider
    message: str
    was_successful: bool
    data: Union[
        PaystackVerificationData, 
        StripeVerificationData,
    ] = field(default_factory=dict)      
        