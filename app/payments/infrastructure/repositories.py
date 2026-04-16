# Repositories to abstract database access for payments and transactions.

from django.contrib.auth.models import AbstractUser
from django.db import transaction, OperationalError
from payments.models.payments import Payment
from payments.domain.entities import PaymentEntity
from payments.domain.enums import PaymentStatus, PaymentType, PaymentPurpose, RegisteredPaymentProvider
from payments.domain.exceptions import PaymentPersistenceError
from payments.domain.errors import PaymentFailure
from payments.domain.policies import PaymentPolicy
from decimal import Decimal, ROUND_HALF_UP
from nanoid import generate
from typing import Union, Tuple

class PaymentRepository:
    """
        Handles persistence logic for Payments. 
        Encapsulates Django ORM to return Domain Entities.
    """
    def __init__(self, user: Union[AbstractUser, None] = None):
        self.user = user
        self.model = Payment
    
    def _generate_payment_reference(self) -> str:
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ref_id = f"SRV-{generate(safe_characters, 15)}"
        return ref_id
    
    def _generate_idempotency_key(self) -> str:
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"
        idm_key = f"{generate(safe_characters, 20)}"
        return idm_key
    
    def _prepare_monetary_amounts(self, base_amount: Decimal, currency: str) -> Tuple[Decimal, int]:
        """
        Helper to handle currency conversion and minor unit calculation using Decimal.
        """
        from constants import USD_TO_NGN_RATE
        
        rate = Decimal(str(USD_TO_NGN_RATE))
        final_decimal = base_amount
        if currency == "NGN":
            final_decimal = (base_amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        minor_units = int((final_decimal * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return final_decimal, minor_units

    def get_by_reference(self, reference: str, lock: bool = False) -> PaymentEntity | None:
        """
        Retrieves a payment entity. used when their's possibility the user might not be logged in
        If lock=True, it uses select_for_update(nowait=True).
        """
        try:
            queryset = self.model.objects.filter(reference=reference)
            if lock:
                queryset = queryset.select_for_update(nowait=True)
            
            db_payment = queryset.first()
            
            if not db_payment:
                return None
            self.user = db_payment.user 
            return self._map_to_entity(db_payment)

        except OperationalError:
            raise PaymentPersistenceError(
                "This transaction is currently being processed. Please wait.",
                code=PaymentFailure.SERVER_BUSY.code,
                title=PaymentFailure.SERVER_BUSY.title
            )
    
    def get_by_reference_for_user(self, reference: str) -> PaymentEntity | None:
        """Retrieves a specific payment for the initialized user."""
        db_obj = self.model.objects.filter(user=self.user, reference=reference).first()
        return self._map_to_entity(db_obj) if db_obj else None

    def find_user_active_payment(self, payment_type: PaymentType, purpose: PaymentPurpose) -> PaymentEntity | None:
        """
            Finds a unique payment record for the user context and maps it to a Domain Entity.

            Guards:
                - Validates that self.user is an authenticated AbstractUser instance.
                - Filters by non-terminal and successful statuses to ensure idempotency.

            Args:
                payment_type (PaymentType): The type of payment to be made as defined in the PaymentType class.
                purpose (PaymentPurpose): The intent/target of the payment.

            Returns:
                Optional[PaymentEntity]: A mapped entity or None if no record matches 
                the specific intent and active status.
        """
        db_obj = self.model.objects.filter(
            user=self.user,
            payment_type=payment_type,
            payment_purpose=purpose,
            status__in=[
                PaymentStatus.INITIATED,
                PaymentStatus.PENDING,
                PaymentStatus.SUCCESS,
            ]
        ).first()
        return self._map_to_entity(db_obj) if db_obj else None

    def create_record(
        self, 
        amount: Decimal, 
        currency: str, 
        payment_type: PaymentType, 
        purpose: PaymentPurpose, 
        provider:RegisteredPaymentProvider,
    ) -> PaymentEntity:
        """
        Persists a new transaction after validating user context and converting currency.

        Operations:
            - Executes `PaymentPolicy` authentication guard.
            - Normalizes `amount` into decimal and minor units (e.g., Kobo).
            - Generates a unique idempotent reference for the gateway.
            - Maps the resulting database object to a domain Entity.

        Args:
            amount: The raw monetary value to process.
            currency: ISO 4217 code (e.g., 'NGN') used for unit conversion.
            payment_type: Categorization as ONE_TIME or SERVICE.
            purpose: The specific business intent of the payment.
            provider: The gateway (e.g., Paystack) handling the request.

        Returns:
            PaymentEntity: The domain-layer representation of the record.
        """
        PaymentPolicy.is_authenticated_user(self.user)
        amount_in_decimal, amount_minor = self._prepare_monetary_amounts(amount, currency)
        db_obj = self.model.objects.create(
            user=self.user,
            reference=self._generate_payment_reference(),
            amount_decimal=amount_in_decimal,
            amount_in_minor_units=amount_minor,
            currency=currency,
            payment_type=payment_type,
            payment_purpose=purpose,
            gateway=provider,
        )
        return self._map_to_entity(db_obj)
        
    def update_as_expired(self, entity: PaymentEntity) -> None:
        """Persists the transition to an EXPIRED state."""
        self.model.objects.filter(user=entity.user, reference=entity.reference).update(
            status=entity.status,
            gateway_response=entity.gateway_response,
        )

    def update_as_successful(self, entity: PaymentEntity) -> None:
        """Persists the transition to a SUCCESS state after verification."""
        
        self.model.objects.filter(reference=entity.reference).update(
            status=entity.status,
            gateway_reference=entity.gateway_reference,
            
            metadata=entity.metadata,
            paid_at=entity.paid_at,
        )
    
    def update_as_initialized(self, entity: PaymentEntity) -> None:
        """
            Persists gateway-generated credentials to allow checkout and session resumption.
        """
        self.model.objects.filter(
            user=entity.user, 
            reference=entity.reference
        ).update(
            gateway_reference=entity.gateway_reference,
            gateway_response=entity.gateway_response,
            metadata=entity.metadata,
        )

    def _map_to_entity(self, model: Payment) -> PaymentEntity:
        """
        Converts a Django Model instance into a Payment Domain Entity.
        """
        return PaymentEntity(
            id=model.id,
            user=model.user,
            reference=model.reference,
            status=model.status,
            amount_decimal=model.amount_decimal,
            amount_in_minor_units=model.amount_in_minor_units,
            currency=model.currency,
            gateway=model.gateway,
            payment_type=model.payment_type,
            payment_purpose=model.payment_purpose,
            gateway_reference=model.gateway_reference,
            gateway_response=model.gateway_response,
            gateway_order_id=model.gateway_order_id,
            metadata=model.metadata,
            created_at=model.created_at,
            paid_at=model.paid_at,
            is_processed=model.is_processed,
        )
