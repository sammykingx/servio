# Core orchestration logic for processing payments regradless of gateway.

from django.contrib.auth.models import AbstractUser
from django.db import transaction, IntegrityError, OperationalError
from payments.infrastructure.registry import GATEWAYS
from payments.infrastructure.repositories import PaymentRepository
from payments.domain.enums import RegisteredPaymentProvider, PaymentPurpose, PaymentStatus, PaymentType, PaymentPhase
from payments.domain.entities import GatewayInitializationResultEntity, PaymentEntity
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
    
    def _build_response(self, payment_entity: PaymentEntity) -> GatewayInitializationResultEntity:
        """Helper to format the final UI response."""
        return GatewayInitializationResultEntity(
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
                if err.code == PaymentFailure.ALREADY_PROCESSED.code:
                    raise err
                if err.code == PaymentFailure.PAYMENT_SESSION_EXPIRED.code:
                    # stale payment
                    existing_entity.mark_as_expired(err.message)
                    self.repo.update_as_expired(existing_entity)

        return self.repo.create_record(amount, self.currency, payment_type, payment_purpose, self.provider)

    def process_payment(self, reference: str) -> GatewayInitializationResultEntity:
        payment_entity = self.repo.get_by_reference(reference)
        PaymentPolicy.ensure_entity_is_processable(payment_entity, phase=PaymentPhase.INITIALIZATION)
        if not payment_entity.is_session_expired:
            return self._build_response(payment_entity)
        
        payload = self.prepare_gateway_entity(payment_entity)
        gw_entity = self.gateway.create_payment(payload)
        payment_entity.sync_gateway_checkout_session(gw_entity)
        return gw_entity

    def verify(self, reference):
        """
            Unified verification logic for both Webhooks and Active Views.
        """
        try:
            payment_entity = self.repo.get_by_reference(reference, lock=True)
            PaymentPolicy.ensure_entity_is_processable(payment_entity, phase=PaymentPhase.VERIFICATION)
            gateway_resp = {'status': True, 'message': 'Verification successful', 'data': {'id': 6029033797, 'domain': 'test', 'status': 'success', 'reference': 'SRV-jSCgCj9KZ0NehGo', 'receipt_number': None, 'amount': 5600000, 'message': "Can't requery test transaction", 'gateway_response': 'Approved', 'paid_at': '2026-04-14T21:35:20.000Z', 'created_at': '2026-04-12T00:42:43.000Z', 'channel': 'bank_transfer', 'currency': 'NGN', 'ip_address': '102.89.85.44', 'metadata': {'cancel_action': '/payments/cancelled/'}, 'log': {'start_time': 1775954798, 'time_spent': 26, 'attempts': 0, 'errors': 0, 'success': True, 'mobile': True, 'input': [], 'history': [{'type': 'action', 'message': 'Set payment method to: bank_transfer', 'time': 61}, {'type': 'action', 'message': 'Set payment method to: card', 'time': 66}, {'type': 'action', 'message': 'Set payment method to: bank_transfer', 'time': 8}, {'type': 'action', 'message': 'Set payment method to: card', 'time': 10}, {'type': 'action', 'message': 'Set payment method to: bank_transfer', 'time': 18}, {'type': 'success', 'message': 'Successfully paid with bank_transfer', 'time': 26}]}, 'fees': 94000, 'fees_split': None, 'authorization': {'authorization_code': 'AUTH_gcpa7yd6xr', 'bin': '123XXX', 'last4': 'X890', 'exp_month': '04', 'exp_year': '2026', 'channel': 'bank_transfer', 'card_type': 'transfer', 'bank': None, 'country_code': 'NG', 'brand': 'Managed Account', 'reusable': False, 'signature': None, 'account_name': None, 'sender_bank': None, 'sender_country': 'NG', 'sender_bank_account_number': 'XXXXXXX890', 'sender_name': 'TEST PAYER', 'narration': 'Test transaction', 'receiver_bank_account_number': None, 'receiver_bank': None}, 'customer': {'id': 355100918, 'first_name': None, 'last_name': None, 'email': 'dylar77@anhmaybietchoi.com', 'customer_code': 'CUS_ge21z2zt8xncvzr', 'phone': None, 'metadata': None, 'risk_action': 'default', 'international_format_phone': None}, 'plan': None, 'split': {}, 'order_id': None, 'paidAt': '2026-04-14T21:35:20.000Z', 'createdAt': '2026-04-12T00:42:43.000Z', 'requested_amount': 5600000, 'pos_transaction_data': None, 'source': None, 'fees_breakdown': None, 'connect': None, 'transaction_date': '2026-04-12T00:42:43.000Z', 'plan_object': {}, 'subaccount': {}}} # self.gateway.verify_payment(reference)
            # update db record
        except OperationalError:
            raise PaymentPersistenceError(
                "Your payment is currently being processed. Please wait a moment before trying again.",
                code=PaymentFailure.SERVER_BUSY.code,
                title=PaymentFailure.SERVER_BUSY.title,
            )
        except PolicyViolationError as err:
            if err.code == PaymentFailure.ALREADY_PROCESSED.code:
                return
            raise err
        return gateway_resp
        # return a unified response
        
        
# {
    # 'status': True, 
    # 'message': 'Verification successful', 
    # 'data': {
        # 'id': 6029033797, 
        # 'domain': 'test', 
        # 'status': 'success', 
        # 'reference': 'SRV-jSCgCj9KZ0NehGo', 
        # 'receipt_number': None, 
        # 'amount': 5600000, 
        # 'message': "Can't requery test transaction", 
        # 'gateway_response': 'Approved', 
        # 'paid_at': '2026-04-14T21:35:20.000Z', 
        # 'created_at': '2026-04-12T00:42:43.000Z', 
        # 'channel': 'bank_transfer', 
        # 'currency': 'NGN', 
        # 'ip_address': '102.89.85.44', 
        # 'metadata': {'cancel_action': '/payments/cancelled/'
    # }, 
    # 'log': {
        # 'start_time': 1775954798, 
        # 'time_spent': 26, 
        # 'attempts': 0, 
        # 'errors': 0, 
        # 'success': True, 
        # 'mobile': True, 
        # 'input': [], 
        # 'history': [{'type': 'action', 'message': 'Set payment method to: bank_transfer', 'time': 61}, {'type': 'action', 'message': 'Set payment method to: card', 'time': 66}, {'type': 'action', 'message': 'Set payment method to: bank_transfer', 'time': 8}, {'type': 'action', 'message': 'Set payment method to: card', 'time': 10}, {'type': 'action', 'message': 'Set payment method to: bank_transfer', 'time': 18}, {'type': 'success', 'message': 'Successfully paid with bank_transfer', 'time': 26}]}, 'fees': 94000, 'fees_split': None, 'authorization': {'authorization_code': 'AUTH_gcpa7yd6xr', 'bin': '123XXX', 'last4': 'X890', 'exp_month': '04', 'exp_year': '2026', 'channel': 'bank_transfer', 'card_type': 'transfer', 'bank': None, 'country_code': 'NG', 'brand': 'Managed Account', 'reusable': False, 'signature': None, 'account_name': None, 'sender_bank': None, 'sender_country': 'NG', 'sender_bank_account_number': 'XXXXXXX890', 'sender_name': 'TEST PAYER', 'narration': 'Test transaction', 'receiver_bank_account_number': None, 'receiver_bank': None}, 'customer': {'id': 355100918, 'first_name': None, 'last_name': None, 'email': 'dylar77@anhmaybietchoi.com', 'customer_code': 'CUS_ge21z2zt8xncvzr', 'phone': None, 'metadata': None, 'risk_action': 'default', 'international_format_phone': None}, 'plan': None, 'split': {}, 'order_id': None, 'paidAt': '2026-04-14T21:35:20.000Z', 'createdAt': '2026-04-12T00:42:43.000Z', 'requested_amount': 5600000, 'pos_transaction_data': None, 'source': None, 'fees_breakdown': None, 'connect': None, 'transaction_date': '2026-04-12T00:42:43.000Z', 'plan_object': {}, 'subaccount': {}}}
