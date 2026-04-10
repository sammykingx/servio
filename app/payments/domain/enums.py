# Enums such as PaymentStatus, EscrowStatus, PaymentProvider.

from enum import Enum

class RegisteredPaymentProvider(str, Enum):
    PAYSTACK = "paystack"
    STRIPE = "stripe"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class PaymentType(str, Enum):
    ONE_TIME = "one_time"
    SERVICE = "service"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
class PaymentStatus(str, Enum):
    INITIATED = "initiated"
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
    
class ChargeStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
    
class EscrowStatus(str, Enum):
    HELD = "held"
    RELEASED = "released"
    REFUNDED = "refunded"
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]