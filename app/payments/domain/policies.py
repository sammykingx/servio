# Business rules like Paymentpolicy, EscrowReleasePolicy, RefundPolicy.

from django.contrib.auth.models import AbstractUser
from payments.domain.enums import PaymentStatus
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import PolicyViolationError
from payments.infrastructure.registry import GATEWAYS
from payments.models.payments import Payment


class PaymentPolicy:
    """
    Enforces business rules regarding payment states and transitions.
    """

    @classmethod
    def validate_for_checkout(cls, payment_obj: Payment | None):
        """
        Ensures a payment is in a valid state to proceed with gateway operations.
        """
        if not payment_obj:
            raise PolicyViolationError(
                message="We couldn't find a record for this payment. Please check your reference number or try again.",
                code=PaymentFailure.INVALID_REFERENCE.code,
                title=PaymentFailure.INVALID_REFERENCE.title,
            )
            
        if payment_obj.status == PaymentStatus.SUCCESS:
            raise PolicyViolationError(
                "We've blocked this extra attempt to ensure you aren't charged twice. You're all set!",
                code=PaymentFailure.ALREADY_PROCESSED.code,
                title=PaymentFailure.ALREADY_PROCESSED.title,
            )
            
    @staticmethod
    def is_authenticated_user(user):
        """Ensures the user initiating the session is valid and attached to a real user account."""
        
        if not user or not isinstance(user, AbstractUser):
            raise PolicyViolationError(
                message="Your session has expired or is invalid. Please log in again.",
                code=PaymentFailure.AUTHENTICATION_REQUIRED.code,
                title=PaymentFailure.AUTHENTICATION_REQUIRED.title
            )

    @staticmethod
    def is_valid_gateway_configuration(provider: str):
        """Ensures the selected payment provider is correctly mapped to an adapter."""
        if provider not in GATEWAYS:
            # Note: This is often a DomainException because it's a dev-config error,
            # but we catch it here to prevent system crashes.
            raise PolicyViolationError(
                message=f"The payment provider '{provider}' is currently unavailable.",
                code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title
            )