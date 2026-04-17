# Business rules like Paymentpolicy, EscrowReleasePolicy, RefundPolicy.

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from payments.domain.enums import PaymentStatus, PaymentPhase, RegisteredPaymentProvider
from payments.domain.entities import PaymentEntity
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import PolicyViolationError
from payments.infrastructure.registry import GATEWAYS
from datetime import timedelta


class PaymentPolicy:
    """
    Enforces business rules regarding payment states and transitions.
    """

    @classmethod
    def ensure_entity_is_processable(cls, payment_entity: PaymentEntity | None, phase: PaymentPhase = PaymentPhase.INITIALIZATION):
        """
        Ensures a payment enetity is in a valid state to proceed with gateway operations.
        """
        if not payment_entity:
            raise PolicyViolationError(
                message="We couldn't find a record for this payment. Please check your reference number or try again.",
                code=PaymentFailure.INVALID_REFERENCE.code,
                title=PaymentFailure.INVALID_REFERENCE.title,
            )
            
        if payment_entity.status == PaymentStatus.SUCCESS:
            msg = (
                "Payment already verified. Your transaction was completed successfully."
                if phase == PaymentPhase.VERIFICATION else
                "This payment has already been completed. We've blocked this attempt to ensure you aren't charged twice."
            )
            raise PolicyViolationError(
                msg,
                code=PaymentFailure.ALREADY_PROCESSED.code,
                title=PaymentFailure.ALREADY_PROCESSED.title,
            )
            
        if phase == PaymentPhase.INITIALIZATION:
            cls._ensure_session_is_not_stale(payment_entity)
            
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
            raise PolicyViolationError(
                message=f"The payment provider '{provider}' is currently unavailable.",
                code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title
            )
    
    @staticmethod
    def _ensure_session_is_not_stale(payment_entity: PaymentEntity):
        """
        Validates that the gateway session (e.g., Paystack access_code) hasn't expired.
        Currently enforces a 4-hour limit for Paystack.
        """
        if payment_entity.gateway == RegisteredPaymentProvider.PAYSTACK:
            exp_time = timezone.now() - payment_entity.created_at
            if exp_time > timedelta(hours=4):
                raise PolicyViolationError(
                    "This payment session has expired. Please refresh the page to start a new transaction.",
                    code=PaymentFailure.PAYMENT_SESSION_EXPIRED.code,
                    title=PaymentFailure.PAYMENT_SESSION_EXPIRED.title,
                )