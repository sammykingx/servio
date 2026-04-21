# Enums such as PaymentStatus, EscrowStatus, PaymentProvider.

from enum import Enum

class RegisteredPaymentProvider(str, Enum):
    PAYSTACK = "paystack"
    STRIPE = "stripe"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class PaymentType(str, Enum):
    """
    Defines the structural nature of a transaction.

    Attributes:
        ONE_TIME: A standalone, non-recurring transaction (e.g., a single purchase).
        SERVICE: A recurring or utility-based payment linked to ongoing access.
    """
    ONE_TIME = "one_time"
    SERVICE = "service"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
class PaymentPurpose(str, Enum):
    """
        Defines the intent of a transaction.
        
        Used as a unique constraint key alongside 'user' and 'status' to 
        idempotently prevent multiple successful payments for the same intent 
        (e.g., ensuring an activation_fee is only paid once).
    """
    ACTIVATION_FEE = "activation_fee"
    SERVICE_PAYMENT = "service_payment"
    WALLET_FUNDING = "wallet_funding"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
class PaymentStatus(str, Enum):
    ABANDONED = "abandoned" # never paid and trying to verify
    INITIATED = "initiated" # newly created
    PENDING = "pending" # payment not verified neither is the amount veririfed
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNDERPAID = "underpaid" # paid but value is below espected amount
    EXPIRED = "expired"
    REFUNDED = "refunded"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
class PaymentPhase(str, Enum):
    INITIALIZATION = "initialization"
    VERIFICATION = "verification"
    
   
# Not in use 
# class ChargeStatus(str, Enum):
#     PENDING = "pending"
#     SUCCESS = "success"
#     FAILED = "failed"
    
#     @classmethod
#     def choices(cls):
#         return [(item.value, item.name) for item in cls]
    

# Escrow not settled  
class EscrowStatus(str, Enum):
    HELD = "held"
    RELEASED = "released"
    REFUNDED = "refunded"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

