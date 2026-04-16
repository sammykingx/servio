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
from decimal import Decimal
from pydantic import ValidationError
from typing import Any, Dict, Union
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
    
    def _build_response(self, payment_entity: PaymentEntity) -> GatewayInitializationResult:
        """Helper to format the final UI response."""
        return GatewayInitializationResult(
           gateway=payment_entity.gateway,
           message=payment_entity.gateway_response,
           data=payment_entity.metadata,
        )
    
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
    
    def initiate_payment(self, amount: Decimal, payment_type: PaymentType, payment_purpose:PaymentPurpose) -> PaymentEntity:
        existing_entity = self.repo.find_user_active_payment(payment_type, payment_purpose)
        if existing_entity:
            try:
                PaymentPolicy.ensure_entity_is_processable(existing_entity, phase=PaymentPhase.INITIALIZATION)
                return existing_entity
            except PolicyViolationError as err:
                if err.code == PaymentFailure.ALREADY_PROCESSED.code:
                    raise err
                if err.code == PaymentFailure.PAYMENT_SESSION_EXPIRED.code:
                    # stale payment
                    existing_entity.mark_as_expired(err.message)
                    self.repo.update_as_expired(existing_entity)

        return self.repo.create_record(amount, self.currency, payment_type, payment_purpose, self.provider)

    def process_payment(self, reference: str) -> GatewayInitializationResult:
        payment_entity = self.repo.get_by_reference(reference)
        PaymentPolicy.ensure_entity_is_processable(payment_entity, phase=PaymentPhase.INITIALIZATION)
        if payment_entity.gateway == RegisteredPaymentProvider.PAYSTACK and payment_entity.gateway_reference:
            # to resume transaction
            return self._build_response(payment_entity)
        
        payload = self.prepare_gateway_entity(payment_entity)
        gw_entity = self.gateway.create_payment(payload)
        payment_entity.sync_initialization(gw_entity)
        # get response json
        return gw_entity

    def verify(self, reference):
        """
            Unified verification logic for both Webhooks and Active Views.
        """
        try:
            payment_entity = self.repo.get_by_reference(reference, lock=True)
            PaymentPolicy.ensure_entity_is_processable(payment_entity, phase=PaymentPhase.VERIFICATION)
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
