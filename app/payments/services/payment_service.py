# Core orchestration logic for processing payments regradless of gateway.

from django.contrib.auth.models import AbstractUser
from django.db import OperationalError
from payments.infrastructure.registry import GATEWAYS
from payments.infrastructure.repositories import PaymentRepository
from payments.domain.enums import (
    RegisteredPaymentProvider, 
    PaymentPurpose, 
    PaymentType, 
    PaymentPhase, 
    PaymentStatus
)
from payments.domain.entities.gateway import GatewayInitResponse, GatewayVerifyResponse
from payments.domain.entities.payments import PaymentEntity
from payments.domain.exceptions import DomainException, PolicyViolationError, PaymentPersistenceError
from payments.domain.errors import PaymentFailure
from payments.domain.policies import PaymentPolicy
from payments.schemas.payments import PaymentGatewayPayload
from decimal import Decimal
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

    def _resolve_gateway_provider(self, payment:PaymentEntity) -> None:
        """
            Synchronizes the active gateway instance with the provider stored in the payment record.
            
            If the payment exists and its gateway differs from the current provider, 
            it re-initializes self.gateway to the correct provider class.
        """
        if payment.gateway != self.provider:
            gateway_class = GATEWAYS.get(payment.gateway)
            if gateway_class:
                self.gateway = gateway_class()
    
    def _build_response(self, payment_entity: PaymentEntity) -> GatewayInitResponse:
        """
        Maps a persisted PaymentEntity back into a standardized 
        GatewayInitResponse which serves as the final data formatter 
        for both fresh and resumed checkout sessions.
        """
        resp = GatewayInitResponse(
           gateway=payment_entity.gateway,
           message=payment_entity.gateway_response,
           data=payment_entity.metadata,
        )
        return resp.payload()
    
    def prepare_gateway_entity(self, entity:PaymentEntity) -> PaymentGatewayPayload:
        """
        Transforms the domain PaymentEntity into a standardized gateway payload.

        This method acts as a bridge between internal logic and external providers,
        normalizing transaction data and ensuring the appropriate gateway implementation
        is resolved before the handshake occurs.
        """
        gw_entity = PaymentGatewayPayload(
            email=self.user.email,
            amount=entity.amount_in_minor_units,
            reference=entity.reference,
            currency=entity.currency
        )
        self._resolve_gateway_provider(entity)
        return gw_entity
    
    def initiate_payment(self, amount: Decimal, payment_type: PaymentType, payment_purpose:PaymentPurpose) -> PaymentEntity:
        """
            Registers the user's payment intent by retrieving a valid existing session or creating a fresh one.

            This internal orchestration ensures idempotency by reusing active records, expiring stale sessions, 
            and preventing duplicate billing before any external gateway handshake occurs.
        """
        existing_entity = self.repo.find_user_active_payment(payment_type, payment_purpose)
        if existing_entity:
            try:
                PaymentPolicy.ensure_entity_is_processable(existing_entity, phase=PaymentPhase.INITIALIZATION)
                return existing_entity
            except PolicyViolationError as err:
                if err.code == PaymentFailure.ALREADY_VERIFIED.code:
                    # for success or incomplete payment status forsame payment intent
                    return existing_entity
                if err.code == PaymentFailure.PAYMENT_SESSION_EXPIRED.code:
                    # stale payment
                    existing_entity.mark_as_expired(err.message)
                    self.repo.update_status(existing_entity)

        return self.repo.create_record(amount, self.currency, payment_type, payment_purpose, self.provider)

    def process_payment(self, reference: str) -> Dict[str, Any]:
        """
        Orchestrates the lifecycle transition from a local record to a gateway checkout.

        This method fetches the transaction and enforces initialization policies. 
        It prioritizes session reuse for active gateway handshakes; if no active 
        session exists, it performs a new provider handshake and persists the 
        resulting checkout metadata.

        Args:
            reference: The unique internal identifier for the transaction.
        Returns:
            GatewayInit: The finalized checkout URL and provider-specific metadata.
        Raises:
            PolicyViolationError: If the transaction is finalized, invalid, or contains 
                a stale gateway session that requires a fresh reference.
        """
        try:
            payment_entity = self.repo.get_by_reference(reference)
            PaymentPolicy.ensure_entity_is_processable(payment_entity, phase=PaymentPhase.INITIALIZATION)
            if payment_entity.has_active_gateway_session:
                return self._build_response(payment_entity)
            
            payload = self.prepare_gateway_entity(payment_entity)
            gw_entity = self.gateway.create_payment(payload)
            payment_entity.sync_gateway_checkout_session(gw_entity)
            self.repo.persist_checkout_session(payment_entity)
            return gw_entity.payload()
        except PolicyViolationError as err:
            raise err

    def verify(self, reference: str) -> GatewayVerifyResponse:
        """
        Coordinates the final verification handshake and persists the transaction outcome.

        This method employs a pessimistic lock on the payment record to ensure atomicity 
        during state transitions. It validates the transaction against verification 
        policies, queries the external gateway for the definitive payment status, 
        and synchronizes the internal entity before releasing the lock.

        Args:
            reference: The unique tracking identifier for the transaction.
        Returns:
            GatewayVerify: A unified data object containing the gateway's 
                verification status and raw metadata.
        Raises:
            PaymentPersistenceError: If the record is currently locked by another 
                process (concurrency protection).
            PolicyViolationError: If the transaction has already been finalized 
                or fails internal integrity checks.
            GatewayError: If the provider is unreachable or returns an invalid response.
        """
        try:
            payment = self.repo.get_by_reference(reference, lock=True)
            PaymentPolicy.ensure_entity_is_processable(payment, phase=PaymentPhase.VERIFICATION)
            PaymentPolicy.ensure_is_not_terminal(payment)
            self._resolve_gateway_provider(payment)
            gw_result = self.gateway.verify_payment(reference)
            self._finalize_verification(payment, gw_result)
            return gw_result

        except OperationalError:
            raise PaymentPersistenceError(
                "Payment is being verified. Please wait a moment before trying again.",
                code=PaymentFailure.SERVER_BUSY.code,
                title=PaymentFailure.SERVER_BUSY.title
            )
        except PolicyViolationError as err:
            raise err

    def _finalize_verification(self, payment: PaymentEntity, gw_result: GatewayVerifyResponse):
        """Handles the state transition logic based on gateway success"""
        if not gw_result.was_successful:
            return self._handle_payment_failure(payment, gw_result)
        
        # success and underpaid transaction verification
        if not payment.is_processed:
            payment.finalize_from_gateway(gw_result)
            self.repo.update_as_successful(payment)
        
    def _handle_payment_failure(self, payment: PaymentEntity, gw_result: GatewayVerifyResponse):
        """
        Branches failure logic between 'Abandoned' and 'Failed' states.
        """
        
        if gw_result.status == PaymentStatus.ABANDONED:
            payment.mark_as_abandoned(
                reason=gw_result.message, 
                metadata=gw_result.data.model_dump(mode="json")
            )
            return self.repo.update_as_abandoned(payment)
        
        payment.mark_as_failed(gw_result.message)
        return self.repo.update_status(payment)
        
# {'status': True, 'message': 'Verification successful', 'data': {'id': 6056669528, 'domain': 'test', 'status': 'success', 'reference': 'SRV-WY0Fnw10r4dwcvl', 'receipt_number': None, 'amount': 2800000, 'message': None, 'gateway_response': 'Successful', 'paid_at': '2026-04-19T23:38:10.000Z', 'created_at': '2026-04-19T23:37:16.000Z', 'channel': 'card', 'currency': 'NGN', 'ip_address': '102.89.46.38', 'metadata': {'cancel_action': '/payments/checkout/cancelled/'}, 'log': {'start_time': 1776641842, 'time_spent': 48, 'attempts': 1, 'errors': 0, 'success': True, 'mobile': True, 'input': [], 'history': [{'type': 'action', 'message': 'Set payment method to: card', 'time': 29}, {'type': 'action', 'message': 'Attempted to pay with card', 'time': 48}, {'type': 'success', 'message': 'Successfully paid with card', 'time': 48}]}, 'fees': 52000, 'fees_split': None, 'authorization': {'authorization_code': 'AUTH_wdu0om86xy', 'bin': '408408', 'last4': '4081', 'exp_month': '12', 'exp_year': '2030', 'channel': 'card', 'card_type': 'visa ', 'bank': 'TEST BANK', 'country_code': 'NG', 'brand': 'visa', 'reusable': True, 'signature': 'SIG_o6DImVqfL5I3m8UjPD3p', 'account_name': None, 'receiver_bank_account_number': None, 'receiver_bank': None}, 'customer': {'id': 355100918, 'first_name': None, 'last_name': None, 'email': 'dylar77@anhmaybietchoi.com', 'customer_code': 'CUS_ge21z2zt8xncvzr', 'phone': None, 'metadata': None, 'risk_action': 'default', 'international_format_phone': None}, 'plan': None, 'split': {}, 'order_id': None, 'paidAt': '2026-04-19T23:38:10.000Z', 'createdAt': '2026-04-19T23:37:16.000Z', 'requested_amount': 2800000, 'pos_transaction_data': None, 'source': None, 'fees_breakdown': None, 'connect': None, 'transaction_date': '2026-04-19T23:37:16.000Z', 'plan_object': {}, 'subaccount': {}}}