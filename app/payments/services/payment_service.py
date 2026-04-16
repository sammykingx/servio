# Core orchestration logic for processing payments regradless of gateway.

from django.contrib.auth.models import AbstractUser
from django.db import transaction, IntegrityError, OperationalError
from payments.infrastructure.registry import GATEWAYS
from payments.infrastructure.repositories import PaymentRepository
from payments.domain.enums import RegisteredPaymentProvider, PaymentPurpose, PaymentStatus, PaymentType, PaymentPhase
from payments.domain.entities import GatewayInitializationResult, PaymentEntity
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

    def __init__(self, gateway_name: RegisteredPaymentProvider, phase: PaymentPhase, user: Union[AbstractUser, None] = None):
        try:
            self.provider = RegisteredPaymentProvider(gateway_name)
            if self.provider not in GATEWAYS:
                raise DomainException(
                    f"Gateway '{self.provider}' is registered but has no Adapter.",
                    code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                    title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title
                )
            if phase == PaymentPhase.INITIALIZATION:
                PaymentPolicy.is_authenticated_user(user)
                
            gateway_class = GATEWAYS[self.provider]
            self.user = user
            self.gateway = gateway_class()
            self.repo = PaymentRepository(self.user)
            self.currency = "NGN" if self.provider == RegisteredPaymentProvider.PAYSTACK else "USD"
            
        except ValueError:
            raise DomainException(
                f"'{gateway_name.title()}' is not a supported payment provider.", 
                code=PaymentFailure.UNSUPPORTED_PROVIDER.code, 
                title=PaymentFailure.UNSUPPORTED_PROVIDER.title
            )

    def _resolve_gateway_provider(self, payment_obj:Payment) -> None:
        """
            Synchronizes the active gateway instance with the provider stored in the payment record.
            
            If the payment exists and its gateway differs from the current provider, 
            it re-initializes self.gateway to the correct provider class.
        """
        if payment_obj.gateway != self.provider:
            gateway_class = GATEWAYS.get(payment_obj.gateway)
            if gateway_class:
                self.gateway = gateway_class()
    
    # outsourced to repo      
    def _create_payment_record(self, payment_type:PaymentType, purpose: PaymentPurpose) -> Payment:
        """
            Private helper to handle the actual DB insertion.
            Should not be called directly outside of initiation logic (self.get_or_create_record).
        """
        amount_in_decimal, amount_in_minor_units = self.get_subscription_fee()
        payment_reference = self.generate_payment_reference()
        
        return Payment.objects.create(
            user=self.user,
            reference=payment_reference,
            amount_decimal=amount_in_decimal,
            amount_in_minor_units=amount_in_minor_units,
            currency=self.currency,
            payment_type=payment_type,
            payment_purpose=purpose,
            gateway=self.provider,
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
    
    def prepare_gateway_entity(self, entity:PaymentEntity) -> PaymentGatewayRequest:
        try:
            gw_entity = PaymentGatewayRequest(
                email=self.user.email,
                amount=entity.amount_in_minor_units,
                reference=entity.reference,
                currency=entity.currency
            )
            self._resolve_gateway_provider(entity)
            return gw_entity
        
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
        """Retrieves an exisiting payment obj by reference or returns None using filter/first for brevity."""
        return Payment.objects.filter(user=self.user, reference=reference).first()

                
    @transaction.atomic            
    def sync_gateway_data(self, payment: Payment, gw_resp: dict):
        """
            Synchronizes the local Payment record with the response from the provider during
            initializiation phase of the payment flow.
        """
        try:
            payment = Payment.objects.select_for_update(nowait=True).get(pk=payment.pk)
            data = self._get_gateway_data(payment.gateway, gw_resp)

            payment.gateway_reference = data.get("ref")
            payment.gateway_response = data.get("msg")
            payment.metadata = gw_resp
                
            payment.save(update_fields=["gateway_reference", "gateway_response", "metadata"])
          
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
    
    def get_or_create_payment_record(self, payment_type: PaymentType, payment_purpose:PaymentPurpose) -> Payment:
        """
            Retrieves a valid payment or initializes a new record.

            Logic Flow:
                1. Returns an existing SUCCESS record to prevent double-billing.
                2. Reuses active INITIATED/PENDING records if they pass the freshness policy.
                3. If an existing record is stale (expired), marks it EXPIRED in the DB 
                and falls back to creating a fresh record.

            Raises:
                PolicyViolationError: If a successful payment already exists (ALREADY_PROCESSED) or Payment record is stale
                maening it didn't pass the freshness test.
        """
        existing_payment = Payment.objects.filter(
            user=self.user,
            payment_purpose=payment_purpose,
            status__in=[
                PaymentStatus.INITIATED,
                PaymentStatus.PENDING,
                PaymentStatus.SUCCESS,
            ]
        ).first()

        if existing_payment:
            try:
                PaymentPolicy.ensure_payment_is_processable(existing_payment, phase=PaymentPhase.INITIALIZATION)
                return existing_payment

            except PolicyViolationError as err:
                if err.code == PaymentFailure.ALREADY_PROCESSED.code:
                    raise err
                
                if err.code == PaymentFailure.PAYMENT_SESSION_EXPIRED.code:
                    # stale payment
                    existing_payment.status = PaymentStatus.EXPIRED
                    existing_payment.gateway_response = f"Policy invalidate: {err.message}"
                    existing_payment.save(update_fields=["status", "gateway_response"])

        return self._create_payment_record(payment_type, payment_purpose)

    def process_payment(self, reference: str) -> GatewayInitializationResult:
        payment_entity = self.repo.get_by_reference(reference)
        PaymentPolicy.ensure_payment_is_processable(payment_entity, phase=PaymentPhase.INITIALIZATION)
        if payment_entity.gateway == RegisteredPaymentProvider.PAYSTACK and payment_entity.gateway_reference:
            # to resume transaction
            return payment_entity.metadata
        
        payload = self.prepare_gateway_entity(payment_entity)
        resp_entity = self.gateway.create_payment(payload)
        
        # contnue
        self.sync_gateway_data(payment_entity, resp_entity)
        # get response json
        return resp_entity

    def verify(self, reference):
        """
            Unified verification logic for both Webhooks and Active Views.
        """
        try:
            payment_entity = self.repo.get_by_reference(reference, lock=True)
            PaymentPolicy.ensure_payment_is_processable(payment_entity, phase=PaymentPhase.VERIFICATION)
            self.resolve_gateway_provider(payment_entity)
            gateway_resp = self.gateway.verify_payment(reference)
            # update db record
        except OperationalError:
            raise PaymentPersistenceError(
                "Your payment is currently being processed. Please wait a moment before trying again.",
                code=PaymentFailure.SERVER_BUSY.code,
                title=PaymentFailure.SERVER_BUSY.title,
            )
        return gateway_resp
