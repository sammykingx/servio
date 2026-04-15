# Domain entities like Payment, EscrowTransaction, etc.

from dataclasses import dataclass, field
from datetime import datetime
from payments.domain.enums import PaymentStatus, RegisteredPaymentProvider
from typing import Any, Dict


@dataclass
class PaymentEntity:
    id: str
    user_email: str
    reference: str
    status: PaymentStatus
    amount_in_minor_units: int
    amount_decimal: int
    currency: str   
    gateway: RegisteredPaymentProvider
    payment_type: str
    payment_purpose: str
    created_at: datetime
    
    gateway_reference: str = None
    gateway_response: str = None
    gateway_order_id: int = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_stale(self, hours: int = 4) -> bool:
        """Checks if the payment enetity is stale for paystack"""
        if self.gateway != RegisteredPaymentProvider.PAYSTACK:
            return False
        delta = datetime.now() - self.created_at
        return delta.total_seconds() > (hours * 3600)
    
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.SUCCESS

    def mark_as_expired(self, reason: str):
        self.status = PaymentStatus.EXPIRED
        self.gateway_response = reason
        
    def mark_as_incomplete(self):
        self.status = PaymentStatus.INCOMPLETE
    
    def mark_as_cancelled(self):
        self.status = PaymentStatus.CANCELLED