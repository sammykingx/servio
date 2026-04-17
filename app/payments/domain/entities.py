# Domain entities like Payment, EscrowTransaction, etc.

from django.contrib.auth.models import AbstractUser
from dataclasses import dataclass, field
from datetime import datetime
from payments.domain.enums import PaymentStatus, RegisteredPaymentProvider
from payments.schemas.paystack import PaystackInitializationData
from payments.schemas.stripe import StripeInitializationData
from datetime import timedelta
from typing import Any, Dict, Union
from uuid import UUID


@dataclass(frozen=True)
class GatewayInitializationResultEntity:
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
        
@dataclass(frozen=True)
class GatewayVerificationResultEntity:
    gateway: RegisteredPaymentProvider
    data: dict
            
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
    
    @property
    def is_session_expired(self) -> bool:
        """
        Determines if the payment session has exceeded the gateway's validity window.
        """
        now = datetime.now()
        duration = now - self.created_at
        
        expiry_map = {
            RegisteredPaymentProvider.PAYSTACK: 4,
            RegisteredPaymentProvider.STRIPE: 24,
        }
        
        limit_hours = expiry_map.get(self.gateway, 2)
        return duration > timedelta(hours=limit_hours)
        
    def mark_as_expired(self, reason: str):
        """Domain logic for transitioning to expired state."""
        self.status = PaymentStatus.EXPIRED
        self.gateway_response = f"Platform Policy Violation: {reason}"
            
    def mark_as_successful(self, reason: str, metadata:dict):
        if not self.is_successful():
            self.status = PaymentStatus.SUCCESS
            self.gateway_response=reason,
            self.gateway_order_id="",
            self.metadata=metadata,
            self.paid_at=datetime.now()
            self.is_processed = True
            
    def sync_gateway_checkout_session(self, result: GatewayInitializationResultEntity):
        """
            Synchronizes the entity with the gateway's checkout response to enable session persistence.
            
            This ensures the user can resume the same checkout process if they leave, 
            preventing redundant transaction calls for the same payment intent.
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
        
        