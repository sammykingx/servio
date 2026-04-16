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
        A Domain Entity representing a successful handshake with any 
        Payment Gateway.
        
        This normalizes the varying responses from providers into a 
        consistent format that the PaymentService can process.
    """
    gateway: RegisteredPaymentProvider
    message: str
    data: Union[
        PaystackInitializationData, 
        StripeInitializationData,
        Dict[str, Any]
    ] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.gateway or not self.data:
            raise ValueError("An active payment entity must have a gateway and a gateway data object.")
        
            
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
        
    def is_stale(self, hours: int = 4) -> bool:
        """Checks if the payment enetity is stale for paystack"""
        if self.gateway != RegisteredPaymentProvider.PAYSTACK:
            return False
        delta = datetime.now() - self.created_at
        return delta.total_seconds() > (hours * 3600)
    
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.SUCCESS

    def update_state(self, state: PaymentStatus, reason: str):
        self.status = state
        self.gateway_response = reason
        
    def mark_as_successful(self, reason: str, metadata:dict):
        if self.is_successful():
            return self
        
        self.status = PaymentStatus.SUCCESS
        
        