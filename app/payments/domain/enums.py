# Enums such as PaymentStatus, EscrowStatus, PaymentProvider.

from enum import Enum

class RegisteredPaymentProvider(str, Enum):
    PAYSTACK = "paystack"
    STRIPE = "stripe"
