# Business rules like Paymentpolicy, EscrowReleasePolicy, RefundPolicy.

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from payments.domain.enums import PaymentStatus, PaymentPhase, RegisteredPaymentProvider
from payments.domain.entities.gateway import GatewayVerifyResponse
from payments.domain.entities.payments import PaymentEntity
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import PolicyViolationError
from payments.infrastructure.registry import GATEWAYS
from datetime import timedelta
from decimal import Decimal


class PaymentPolicy:
    """
    Enforces business rules regarding payment states and transitions.
    """
    
    MIN_NGN = Decimal("5000.00")
    MIN_USD = Decimal("20.00")

    @classmethod
    def ensure_entity_is_processable(cls, payment_entity: PaymentEntity | None, phase: PaymentPhase = PaymentPhase.INITIALIZATION):
        """
        Ensures a payment enetity is in a valid state to proceed with gateway operations.
        """
        if not payment_entity:
            raise PolicyViolationError(
                message="We couldn't find a record for this payment. Please check your reference number and try again.",
                code=PaymentFailure.INVALID_REFERENCE.code,
                title=PaymentFailure.INVALID_REFERENCE.title,
            )
            
        if payment_entity.status in {PaymentStatus.SUCCESS, PaymentStatus.UNDERPAID}:
            msg = (
                "Payment already verified. Your transaction was completed successfully."
                if phase == PaymentPhase.VERIFICATION else
                "This payment has already been processed. We've blocked this attempt to ensure you aren't charged twice."
            )
            raise PolicyViolationError(
                msg,
                code=PaymentFailure.ALREADY_VERIFIED.code,
                title=PaymentFailure.ALREADY_VERIFIED.title,
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
        Enforces time-to-live (TTL) constraints on existing gateway sessions.

        Prevents 'Duplicate Reference' errors by ensuring that any existing 
        provider handshake is still within the gateway's acceptance window. 
        If expired, it mandates a full transaction restart.
        """
        if payment_entity.gateway == RegisteredPaymentProvider.PAYSTACK:
            exp_time = timezone.now() - payment_entity.created_at
            if exp_time > timedelta(hours=4):
                raise PolicyViolationError(
                    "This payment session has expired. Please refresh the page to start a new transaction.",
                    code=PaymentFailure.PAYMENT_SESSION_EXPIRED.code,
                    title=PaymentFailure.PAYMENT_SESSION_EXPIRED.title,
                )
                
    @staticmethod
    def validate_paid_amount(payment_entity: PaymentEntity, gw_entity: GatewayVerifyResponse):
        """Ensures the final captured amount matches the processed amount by gateway."""
        if gw_entity.gateway == RegisteredPaymentProvider.PAYSTACK:
            actual_paid_decimal = Decimal(gw_entity.data.amount) / Decimal(100)
            payment_entity.amount_decimal != actual_paid_decimal
            raise PolicyViolationError(
                f"Amount mismatch: Expected {payment_entity.currency}{payment_entity.amount_decimal:.2f}, "
                f"but gateway reported {payment_entity.currency}{actual_paid_decimal:.2f}.",
                code=PaymentFailure.PAYMENT_INCOMPLETE.code,
                title=PaymentFailure.PAYMENT_INCOMPLETE.title
            )
            
    @classmethod
    def validate_minimum_amount(cls, amount: Decimal, currency: str):
        currency = currency.upper()

        if currency == "NGN":
            if amount < cls.MIN_NGN:
                raise PolicyViolationError(
                    f"Minimum NGN payment is ₦{cls.MIN_NGN:,.2f}",
                    code=PaymentFailure.AMOUNT_TOO_LOW.code,
                    title=PaymentFailure.AMOUNT_TOO_LOW.title
                )
        
        elif currency == "USD":
            if amount < cls.MIN_USD:
                raise PolicyViolationError(
                    f"Minimum USD payment is ${cls.MIN_USD:,.2f}",
                    code=PaymentFailure.AMOUNT_TOO_LOW.code,
                    title=PaymentFailure.AMOUNT_TOO_LOW.title
                )

        else:
            raise PolicyViolationError(f"Currency {currency} is not supported.")
        
            
    def ensure_is_not_terminal(entity: PaymentEntity):
        """
        Ensures the payment isn't already locked into a failure/abandoned state.
        
        Raises:
            PolicyViolationError: If the transaction was already definitively verified.
        """
        terminal_statuses = {
            PaymentStatus.FAILED, 
            PaymentStatus.ABANDONED, 
        }
        
        if bool(entity.gateway_reference) and entity.status in terminal_statuses:
            raise PolicyViolationError(
                message=(
                    f"This transaction was verified as {entity.status}. "
                    "No further action is required."
                ),
                code=PaymentFailure.ALREADY_VERIFIED.code,
                title="Verification Completed"
            )
            