# Core orchestration logic for processing payments regradless of gateway.

from django.http import HttpResponseRedirect
from django.contrib.auth.models import AbstractUser
from payments.infrastructure.registry import GATEWAYS
from payments.domain.enums import RegisteredPaymentProvider
from payments.domain.exceptions import DomainException, PolicyViolationError
from payments.domain.errors import PaymentFailure
from payments.domain.enums import PaymentPurpose, PaymentStatus, PaymentType
from payments.schemas.payments import PaymentRequest
from registry_utils import get_registered_model
from nanoid import generate
from pydantic import ValidationError


Payment = get_registered_model("payments", "Payment")

class PaymentService:

    def __init__(self, gateway_name: RegisteredPaymentProvider, user: AbstractUser):
        try:
            self.provider = RegisteredPaymentProvider(gateway_name)
            if self.provider not in GATEWAYS:
                raise DomainException(
                    f"Gateway '{self.provider}' is registered but has no Adapter.",
                    code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                    title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title
                )
            if not user or not isinstance(user, AbstractUser):
                raise PolicyViolationError(
                    "An authenticated user is required to initiate payment.",
                    code=PaymentFailure.AUTHENTICATION_REQUIRED.code,
                    title=PaymentFailure.AUTHENTICATION_REQUIRED.title
                ) 

            gateway_class = GATEWAYS[self.provider]
            self.user = user
            self.gateway = gateway_class()
            self.currency = "NGN" if self.provider == RegisteredPaymentProvider.PAYSTACK else "USD"
            self.payment_reference = None
            self.amount_in_decimal = None
            self.amount_in_minor_units = None
            
        except ValueError:
            raise DomainException(
                f"'{gateway_name.title()}' is not a supported payment provider.", 
                code=PaymentFailure.UNSUPPORTED_PROVIDER.code, 
                title=PaymentFailure.UNSUPPORTED_PROVIDER.title
            )

    def _prepare_payment_payload(self, payment_obj):
        try:
            payload = PaymentRequest(
                email=self.user.email,
                amount=payment_obj.amount_in_minor_units,
                reference=payment_obj.reference,
                currency=self.currency
            )
            return payload
        except ValidationError as err:
            raise PolicyViolationError(
                "The payment information provided is invalid or incomplete.",
                code=PaymentFailure.INVALID_PAYMENT_DATA.code,
                title=PaymentFailure.INVALID_PAYMENT_DATA.title,
                
            )
            
    def generate_payment_reference(self):
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ref_id = f"SRV-{generate(safe_characters, 15)}"
        return ref_id
    
    def generate_idempotency_key(self):
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"
        idm_key = f"{generate(safe_characters, 20)}"
        return idm_key

    def get_subscription_fee(self):
        """Returns the subsription fee in the appropriate currency and minor units based on the gateway."""
        
        from constants import APP_SUBSCRIPTION_FEE, USD_TO_NGN_RATE
        
        if self.provider == RegisteredPaymentProvider.PAYSTACK:
            ngn_amount = APP_SUBSCRIPTION_FEE * USD_TO_NGN_RATE
            amount_in_minor_units = int(ngn_amount * 100)
            return ngn_amount, amount_in_minor_units
        
        return APP_SUBSCRIPTION_FEE, int(APP_SUBSCRIPTION_FEE * 100)
    
    def get_or_create_activation_payment(self):
        existing = Payment.objects.filter(
            user=self.user,
            payment_purpose=PaymentPurpose.ACTIVATION_FEE,
            status__in=[
                PaymentStatus.INITIATED,
                PaymentStatus.PENDING
            ]
        ).first()
        # if status is pending then verify
        if existing:
            return existing
        
        self.amount_in_decimal, self.amount_in_minor_units = self.get_subscription_fee()
        self.payment_reference = self.generate_payment_reference()
        
        return Payment.objects.create(
            user=self.user,
            reference=self.payment_reference,
            amount_decimal=self.amount_in_decimal,
            amount_in_minor_units=self.amount_in_minor_units,
            currency=self.currency,
            payment_type=PaymentType.ONE_TIME,
            payment_purpose=PaymentPurpose.ACTIVATION_FEE,
            gateway=self.provider,
        )

    def process_one_time_payment(self) -> HttpResponseRedirect:
        """Orchestrates the payment creation process regradless of the underlying gateway(stripe or paystack)."""

        payment_obj = self.get_or_create_activation_payment()
        payload = self._prepare_payment_payload(payment_obj)
        return self.gateway.create_payment(payload)
        # returns the checkout url

    def verify(self, reference):

        return self.gateway.verify_payment(reference)
