# payments/schemas/payment.py

from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any
from decimal import Decimal


class PaymentRequest(BaseModel):
    """
    Standardized schema for payment initialization across all gateways.

    This model enforces data integrity for financial transactions, ensuring 
    that mandatory fields like idempotency keys and unique references are 
    validated before reaching the payment provider gateway class (Stripe, Paystack, etc.).

    Attributes:
        email (EmailStr): The customer's verified email address for receipts and tracking.
        amount (int): The transaction value in the smallest currency unit 
            (e.g., kobo for NGN, cents for USD). Must be greater than 0.
        reference (str): A unique, 12-character string used to identify and 
            reconcile the transaction in internal systems.
        idm_key (str): A unique idempotency key. Used to ensure that 
            retried requests do not result in duplicate charges.
        currency (str): The ISO 4217 three-letter currency code. Defaults to "USD".
        metadata (Dict[str, Any]): A flexible dictionary for gateway-specific 
            parameters or additional context (e.g., custom cart data).
    """
    email: EmailStr = Field(..., description="Customer's email address")
    amount: int = Field(..., gt=0, description="Amount in smallest unit (e.g kobo, cents)")
    reference: str = Field(..., min_length=19, max_length=19, description="Unique reference for the transaction")
    # idm_key: str = Field(..., description="Idempotency key to prevent double charging")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    