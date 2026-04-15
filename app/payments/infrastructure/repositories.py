# Repositories to abstract database access for payments and transactions.

from django.contrib.auth.models import AbstractUser
from django.db import transaction, OperationalError
from payments.models.payments import Payment
from payments.domain.entities import PaymentEntity
from payments.domain.enums import PaymentStatus, PaymentPurpose
from payments.domain.exceptions import PaymentPersistenceError
from payments.domain.errors import PaymentFailure
from nanoid import generate
from typing import Union

class PaymentRepository:
    """
        Handles persistence logic for Payments. 
        Encapsulates Django ORM to return Domain Entities.
    """
    def __init__(self, user: Union[AbstractUser, None] = None):
        self.user = user
    
    def _generate_payment_reference(self) -> str:
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ref_id = f"SRV-{generate(safe_characters, 15)}"
        return ref_id
    
    def _generate_idempotency_key(self) -> str:
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"
        idm_key = f"{generate(safe_characters, 20)}"
        return idm_key

    def get_by_reference(self, reference: str, lock: bool = False) -> PaymentEntity | None:
        """
        Retrieves a payment entity. 
        If lock=True, it uses select_for_update(nowait=True).
        """
        try:
            queryset = Payment.objects.filter(reference=reference)
            if lock:
                # Critical for preventing race conditions between Webhook and View
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
        db_obj = Payment.objects.filter(user=self.user, reference=reference).first()
        return self._map_to_entity(db_obj) if db_obj else None

    def find_active_record(self, purpose: PaymentPurpose) -> PaymentEntity | None:
        """Finds existing records that are potentially reusable."""
        db_obj = Payment.objects.filter(
            user=self.user,
            payment_purpose=purpose,
            status__in=[
                PaymentStatus.INITIATED,
                PaymentStatus.PENDING,
                PaymentStatus.SUCCESS,
            ]
        ).first()
        return self._map_to_entity(db_obj) if db_obj else None

    def create_record(self, **data) -> PaymentEntity:
        """Simple wrapper for creation."""
        
        db_obj = Payment.objects.create(
            user=self.user,
            reference=self._generate_payment_reference(),
        )
        return self._map_to_entity(db_obj)

    def update_status(self, reference: str, status: PaymentStatus, gateway_response: str):
        """Specifically updates the status and message."""
        Payment.objects.filter(reference=reference).update(
            status=status,
            gateway_response=gateway_response
        )

    # def save(self, entity: PaymentEntity) -> None:
    #     """
    #     Persists the Domain Entity back to the Django database.
    #     """
    #     Payment.objects.update_or_create(
    #         reference=entity.reference,
    #         defaults={
    #             "status": entity.status,
    #             "gateway_reference": entity.gateway_reference,
    #             "gateway_response": entity.gateway_response,
    #             "metadata": entity.matadata,
    #             "amount_decimal": entity.amount_decimal,
    #             "currency": entity.currency,
    #             "is_processed": entity.is_processed,
    #         }
    #     )

    def _map_to_entity(self, model: Payment) -> PaymentEntity:
        """
        Converts a Django Model instance into a Domain Entity.
        """
        return PaymentEntity(
            id=model.id,
            user_email=model.user,
            reference=model.reference,
            amount_decimal=model.amount_decimal,
            amount_in_minor_units=model.amount_in_minor_units,
            status=model.status,
            gateway=model.gateway,
            gateway_reference=model.gateway_reference,
            gateway_response=model.gateway_response,
            metadata=model.metadata,
            created_at=model.created_at
        )
