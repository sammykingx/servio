# Core orchestration logic for processing payments regradless of gateway.

from django.http import HttpResponseRedirect
from django.contrib.auth.models import AbstractUser
from payments.infrastructure.registry import GATEWAYS
from payments.domain.enums import RegisteredPaymentProvider, PaymentPurpose, PaymentStatus, PaymentType
from payments.domain.exceptions import DomainException, PolicyViolationError
from payments.domain.errors import PaymentFailure
from payments.domain.policies import PaymentPolicy
from payments.models.payments import Payment
from payments.schemas.payments import PaymentGatewayRequest
from nanoid import generate
from pydantic import ValidationError
from typing import Dict, Union


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
            PaymentPolicy.is_authenticated_user(user)
            gateway_class = GATEWAYS[self.provider]
            self.user = user
            self.gateway = gateway_class()
            self.currency = "NGN" if self.provider == RegisteredPaymentProvider.PAYSTACK else "USD"
            
        except ValueError:
            raise DomainException(
                f"'{gateway_name.title()}' is not a supported payment provider.", 
                code=PaymentFailure.UNSUPPORTED_PROVIDER.code, 
                title=PaymentFailure.UNSUPPORTED_PROVIDER.title
            )

    def _prepare_gateway_payload(self, payment_obj:Payment) -> PaymentGatewayRequest:
        try:
            payload = PaymentGatewayRequest(
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
            
    def generate_payment_reference(self) -> str:
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ref_id = f"SRV-{generate(safe_characters, 15)}"
        return ref_id
    
    def generate_idempotency_key(self) -> str:
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
    
    def get_payment_obj(self, reference: str) -> Union[Payment, None]:
        """Retrieves a payment or returns None using filter/first for brevity."""
        return Payment.objects.filter(user=self.user, reference=reference).first()

    def sync_gateway_with_payment(self, ref: str) -> None:
        """
            Synchronizes the active gateway instance with the provider stored in the payment record.
            
            If the payment exists and its gateway differs from the current provider, 
            it re-initializes self.gateway to the correct provider class.
        """
        payment_obj = self.get_payment_obj(ref)
        if not payment_obj:
            return
        
        if payment_obj.gateway != self.provider:
            gateway_class = GATEWAYS.get(payment_obj.gateway)
            if gateway_class:
                self.gateway = gateway_class()
    
    def get_or_initiate_activation_payment(self) -> Payment:
        """
            Retrieves an existing valid activation payment or creates a new one.
            
            Checks for an existing payment with INITIATED, PENDING, or SUCCESS status.
            If found, returns the existing record to prevent duplicate billings.
            Otherwise, generates a new payment reference and creates a fresh 
            activation record.
        """
        existing_payment = Payment.objects.filter(
            user=self.user,
            payment_purpose=PaymentPurpose.ACTIVATION_FEE,
            status__in=[
                PaymentStatus.INITIATED,
                PaymentStatus.PENDING,
                PaymentStatus.SUCCESS,
            ]
        ).first()

        if existing_payment:
            return existing_payment

        amount_in_decimal, amount_in_minor_units = self.get_subscription_fee()
        payment_reference = self.generate_payment_reference()
        
        return Payment.objects.create(
            user=self.user,
            reference=payment_reference,
            amount_decimal=amount_in_decimal,
            amount_in_minor_units=amount_in_minor_units,
            currency=self.currency,
            payment_type=PaymentType.ONE_TIME,
            payment_purpose=PaymentPurpose.ACTIVATION_FEE,
            gateway=self.provider,
        )

    def process_one_time_payment(self, reference: str) -> Dict[str, str]:
        payment_obj = self.get_payment_obj(reference)
        PaymentPolicy.validate_for_checkout(payment_obj)
        payload = self._prepare_gateway_payload(payment_obj)
        self.sync_gateway_with_payment()
        return self.gateway.create_payment(payload)
        # returns the checkout url

    def verify(self, reference):

        return self.gateway.verify_payment(reference)
