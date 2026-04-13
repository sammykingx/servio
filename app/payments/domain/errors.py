from typing import NamedTuple


class FailureDetail(NamedTuple):
    """
    A structured representation of a domain failure.

    Attributes:
        code (str): A unique, machine-readable string identifier (e.g., 'INVALID_AMOUNT').
        title (str): A brief, human-readable description intended for end-user display.
    """

    code: str
    title: str

  
class PaymentFailure:
    UNSUPPORTED_PROVIDER = FailureDetail(
        "UNSUPPORTED_PROVIDER", "Payment Method Not Supported"
    )
    PROVIDER_NOT_CONFIGURED = FailureDetail(
        "PROVIDER_NOT_CONFIGURED", "Gateway Configuration Missing"
    )
    GATEWAY_TIMEOUT = FailureDetail(
        "GATEWAY_TIMEOUT", "Payment Gateway Timed Out"
    )
    GATEWAY_ERROR = FailureDetail(
        "GATEWAY_ERROR", "Gateway Temporarily Unavailable"
    )
    INVALID_PAYMENT_DATA = FailureDetail(
        "INVALID_PAYMENT_DATA", 
        "Incomplete Payment Information"
    )
    INVALID_REFERENCE = FailureDetail(
        "INVALID_REFERENCE", "Invalid Payment Reference"
    )
    ALREADY_PROCESSED = FailureDetail(
        "ALREADY_PROCESSED", "Payment Already Received"
    )
    AUTHENTICATION_REQUIRED = FailureDetail(
        "AUTHENTICATION_REQUIRED", "User Session Invalid"
    )
