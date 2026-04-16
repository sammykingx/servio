# Domain entities like Payment, EscrowTransaction, etc.

from django.contrib.auth.models import AbstractUser
from dataclasses import dataclass, field
from datetime import datetime
from payments.domain.enums import PaymentStatus, RegisteredPaymentProvider
from payments.schemas.paystack import PaystackInitializationData
from payments.schemas.stripe import StripeInitializationData
from typing import Any, Dict, Union
from uuid import UUID


@dataclass(frozen=True)
class GatewayInitializationResult:
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
        PaystackInitializationData, 
        StripeInitializationData,
    ] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.gateway or not self.data:
            raise ValueError("Gateway result must include both a provider and response data.")
            
@dataclass
class PaymentEntity:
    id: UUID
    user: AbstractUser
    reference: str
    status: PaymentStatus
    amount_in_minor_units: int
    amount_decimal: int
    currency: str   
    gateway: RegisteredPaymentProvider
    payment_type: str
    payment_purpose: str
    created_at: datetime
    is_processed: bool
    
    gateway_reference: str = None
    gateway_response: str = None
    gateway_order_id: int = None
    paid_at: datetime = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    
    def _complete_paystack_trx(self, payload):
        pass
    
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.SUCCESS
        
    def mark_as_expired(self, reason: str):
        """Domain logic for transitioning to expired state."""
        self.status = PaymentStatus.EXPIRED
        self.gateway_response = f"Platform Policy Violation: {reason}"
            
    def mark_as_successful(self, reason: str, metadata:dict):
        if not self.is_successful():
            self.status = PaymentStatus.SUCCESS
            self.paid_at=datetime.now()
            
    def sync_initialization(self, result: GatewayInitializationResult):
        """
        Handles syncing for the START of a payment.
        Focus: Extracting access codes/URLs to get the user to the gateway.
        """
        self.gateway_response = result.message
        self.metadata = result.data.model_dump()
        if self.gateway == RegisteredPaymentProvider.PAYSTACK:
            self.gateway_reference = result.data.access_code
            
        elif self.gateway == RegisteredPaymentProvider.STRIPE:
            pass

    # def sync_verification(self, result: GatewayVerificationResult):
    #     """
    #     Handles syncing for the END of a payment (Webhook or Redirect).
    #     Focus: Finalizing status and recording the gateway's internal transaction ID.
    #     """
    #     self.gateway_response = result.message
    #     # We might merge verification data into existing metadata or replace it
    #     self.metadata.update({"verification": result.data})
        
    #     data = result.data if isinstance(result.data, dict) else result.data.dict()

    #     if self.gateway == RegisteredPaymentProvider.PAYSTACK:
    #         # For Paystack verification, the 'reference' we sent is confirmed, 
    #         # and they provide a 'id' for the successful log.
    #         self.gateway_transaction_id = data.get("id") 
    #         self.status = PaymentStatus.SUCCESS if data.get("status") == "success" else PaymentStatus.FAILED
        
        