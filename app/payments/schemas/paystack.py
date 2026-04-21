from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Any, Dict, Union

class PaystackInitData(BaseModel):
    """The actual payload containing checkout details."""
    authorization_url: HttpUrl
    access_code: str
    reference: str

class PaystackInitResponseSchema(BaseModel):
    """The full API response structure from Paystack initialization API."""
    message: str
    data: PaystackInitData

class PaystackVerificationData(BaseModel):
    """
    Represents the validated core transaction data returned by the Paystack 
    verification endpoint.

    This model parses and validates the 'data' object within a Paystack 
    API response, ensuring types are correct for database insertion or 
    business logic processing.

    Attributes:
        id (int): The unique Paystack transaction identifier. A successful 
            assignment indicates the transaction was recognized by the gateway.
        status (str): The current state of the transaction. Expected values 
            typically include 'success', 'failed', or 'abandoned'.
        amount (int): The transaction amount in the currency's minor units 
            (e.g., kobo for NGN or cents for USD). To get the standard unit, 
            divide by 100.
        paid_at (Union[datetime, None]): The ISO 8601 timestamp indicating 
            when the gateway confirmed the payment. Will be None if the 
            transaction is not completed.
        paystack_metadata (Dict[str, Any]): The raw JSON response from the 
            verification endpoint. Useful for auditing or accessing custom 
            fields sent during checkout. Defaults to an empty dictionary.
    """
    id: int
    status: str
    amount:  int
    paid_at: Union[datetime, None]
    paystack_metadata: Dict[str, Any] = Field(default_factory=dict)
