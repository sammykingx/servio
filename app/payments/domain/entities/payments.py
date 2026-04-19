from django.contrib.auth.models import AbstractUser
from dataclasses import dataclass, field
from datetime import datetime
from payments.domain.enums import PaymentStatus, RegisteredPaymentProvider
from payments.schemas.paystack import PaystackVerificationData
from datetime import timedelta
from typing import Any, Dict
from uuid import UUID
from .gateway import GatewayInitResponse, GatewayVerifyResponse


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
    
    paid_amount_in_minor: int = None
    gateway_reference: str = None
    gateway_response: str = None
    gateway_order_id: int = None
    paid_at: datetime = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)    
    
    @property
    def has_active_gateway_session(self) -> bool:
        """Returns True only if the handshake has already occurred (gateway_reference is set)"""
        return bool(self.gateway_reference)
    
    @property
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.SUCCESS
    
    # def is_session_valid(self) -> bool:
    # noneed since policy ensures it's withing the gateway specific
    # time windowk
    #     """
    #     Determines if the payment session has exceeded the gateway's validity window.
    #     """
    #     now = datetime.now()
    #     duration = now - self.created_at
        
    #     expiry_map = {
    #         RegisteredPaymentProvider.PAYSTACK: 4,
    #         RegisteredPaymentProvider.STRIPE: 24,
    #     }
        
    #     limit_hours = expiry_map.get(self.gateway, 4)
    #     return duration < timedelta(hours=limit_hours)
    
    def _transition_to_terminal_failure(self, status: PaymentStatus, reason: str):
        """Private helper to handle shared terminal state logic."""
        self.status = status
        self.gateway_response = reason
        
    def mark_as_expired(self, reason: str):
        """Domain logic for transitioning to an expired state."""
        self._transition_to_terminal_failure(PaymentStatus.EXPIRED, f"Platform Policy Violation: {reason}")
        
    def mark_as_failed(self, reason:str):
        """Domain logic for transitioning to a failed state."""
        self._transition_to_terminal_failure(PaymentStatus.FAILED, reason)
            
    def sync_gateway_checkout_session(self, result: GatewayInitResponse):
        """
            Synchronizes the entity with the gateway's checkout response to enable session persistence.
            
            This ensures the user can resume the same checkout process if they leave, 
            preventing redundant transaction calls for the same payment intent.
        """
        self.gateway_response = result.message
        self.metadata = result.data.model_dump(mode="json")
        if self.gateway == RegisteredPaymentProvider.PAYSTACK:
            self.gateway_reference = result.data.access_code
            
        elif self.gateway == RegisteredPaymentProvider.STRIPE:
            pass
        
    def finalize_from_gateway(self, gw_entity: GatewayVerifyResponse):
        """
            Synchronizes the entity state with a successful gateway verification.

            This method acts as the final state transition, updating the internal 
            reference, capturing gateway metadata, and marking the transaction 
            as successful or incomplete.
        """
        if self.amount_in_minor_units != gw_entity.data.amount:
            self.status = PaymentStatus.INCOMPLETE
        else:
            self.status = PaymentStatus.SUCCESS
            
        self.gateway_response = gw_entity.message
        self.is_processed = True
        
        # paystack part
        self.paid_amount_in_minor = gw_entity.data.amount
        self.paid_at = gw_entity.data.paid_at
        self.gateway_order_id = gw_entity.data.id
        self.metadata = gw_entity.data.paystack_metadata
        
    def _complete_paystack_payment(self, data: PaystackVerificationData):
        """
        Handles syncing for the END of a payment (Webhook or Redirect).
        Focus: Finalizing status and recording the gateway's internal transaction ID.
        """
        pass
    