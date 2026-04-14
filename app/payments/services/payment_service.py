# Core orchestration logic for processing payments regradless of gateway.

from django.contrib.auth.models import AbstractUser
from django.db import transaction, IntegrityError, OperationalError
from payments.infrastructure.registry import GATEWAYS
from payments.domain.enums import RegisteredPaymentProvider, PaymentPurpose, PaymentStatus, PaymentType
from payments.domain.exceptions import DomainException, PolicyViolationError, PaymentPersistenceError
from payments.domain.errors import PaymentFailure
from payments.domain.policies import PaymentPolicy
from payments.models.payments import Payment
from payments.schemas.payments import PaymentGatewayRequest
from nanoid import generate
from pydantic import ValidationError
from typing import Dict, Union
import logging


logger = logging.getLogger("app_file")


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
            
    def _get_gateway_data(self, gateway_name: str, gw_resp: dict) -> Dict[str, str]:
        """
        Private helper to normalize gateway responses into a standard format.
        """
        extractors = {
            RegisteredPaymentProvider.PAYSTACK: lambda resp: {
                "ref": resp.get("data", {}).get("access_code"),
                "msg": resp.get("message"),
            },
            
            # RegisteredPaymentProvider.STRIPE: lambda resp: {
            #     "ref": resp.get("id"),
            #     "msg": resp.get("status")
            # },
        }

        extractor = extractors.get(gateway_name)
        if not extractor:
            raise DomainException(
                "This payment provider is not supported at the moment. Please try a different provider.",
                code=PaymentFailure.UNSUPPORTED_PROVIDER.code,
                title=PaymentFailure.UNSUPPORTED_PROVIDER.title,
                err_type="error",
            )
            
        return extractor(gw_resp)
            
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

    def resolve_gateway_provider(self, payment_obj:Payment) -> None:
        """
            Synchronizes the active gateway instance with the provider stored in the payment record.
            
            If the payment exists and its gateway differs from the current provider, 
            it re-initializes self.gateway to the correct provider class.
        """
        if payment_obj.gateway != self.provider:
            gateway_class = GATEWAYS.get(payment_obj.gateway)
            if gateway_class:
                self.gateway = gateway_class()
                
    @transaction.atomic            
    def sync_gateway_data(self, payment: Payment, gw_resp: dict):
        """
        Synchronizes the local Payment record with the response from the provider.
        """
        
        try:
            payment = Payment.objects.select_for_update().get(pk=payment.pk)
            data = self._get_gateway_data(payment.gateway, gw_resp)

            payment.gateway_reference = data.get("ref")
            payment.gateway_response = data.get("msg")
            payment.metadata = gw_resp
                
            payment.save(update_fields=["gateway_reference", "gateway_response", "metadata", "updated_at"])
          
        except OperationalError:
            raise PaymentPersistenceError(
                "We're still finishing up your previous request. Please wait a moment while we sync your checkout details.",
                code=PaymentFailure.SERVER_BUSY.code,
                title=PaymentFailure.SERVER_BUSY.title,
            )
          
        except IntegrityError:
            raise PaymentPersistenceError(
                "We’re having trouble syncing gateway response to our system. No funds have been moved, please try again or contact support.",
                code=PaymentFailure.DATA_SYNC_CONFLICT.code,
                title=PaymentFailure.DATA_SYNC_CONFLICT.title,
            )
        
        except Exception as err:
            logger.error(err)
            raise err  
    
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
        
        # can continue failed or cancelled payments so long it's within 6h

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
        if payment_obj.gateway == RegisteredPaymentProvider.PAYSTACK and payment_obj.gateway_reference:
            # to resume transaction
            return payment_obj.metadata
        
        payload = self._prepare_gateway_payload(payment_obj)
        self.resolve_gateway_provider(payment_obj)
        resp = self.gateway.create_payment(payload)
        self.sync_gateway_data(payment_obj, resp)
        return resp
        # returns the checkout url

    def verify(self, reference):

        return self.gateway.verify_payment(reference)
