# Core orchestration logic for processing payments regradless of gateway.


from payments.infrastructure.registry import GATEWAYS
from payments.domain.enums import RegisteredPaymentProvider
from payments.domain.exceptions import DomainException, PolicyViolationError
from payments.domain.errors import PaymentFailure
from payments.schemas.payments import PaymentRequest
from nanoid import generate


class PaymentService:

    def __init__(self, gateway_name: RegisteredPaymentProvider):
        try:
            self.provider = RegisteredPaymentProvider(gateway_name)
            if self.provider not in GATEWAYS:
                raise DomainException(
                    f"Gateway '{self.provider}' is registered but has no Adapter.",
                    code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                    title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title
                )

            gateway_class = GATEWAYS[self.provider]
            self.gateway = gateway_class()
            
        except ValueError:
            raise DomainException(
                f"'{gateway_name.title()}' is not a supported payment provider.", 
                code=PaymentFailure.UNSUPPORTED_PROVIDER.code, 
                title=PaymentFailure.UNSUPPORTED_PROVIDER.title
            )
            
    def _create_reference(self):
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ref_id = f"SRV-{generate(safe_characters, 15)}"
        return ref_id
    
    def _create_idempotency_key(self):
        safe_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"
        idm_key = f"{generate(safe_characters, 20)}"
        return idm_key

    def _prepare_payment_payload(self, client_obj, metadata):
        payload = PaymentRequest(
            email=client_obj.email,
            amount=client_obj.amount,
            reference=self._create_reference(),
            metadata=metadata
        )
        return payload.model_dump()

    def charge(self, client_obj, metadata):
        """Orchestrates the payment creation process regradless of the underlying gateway(stripe or paystack)."""

        # check if the client has a payment record with
        # any of the provider
        # prepare the payment object and metadata
        payload = self._prepare_payment_payload(client_obj, metadata)
        return self.gateway.create_payment(payload)
        # create customer if they don't exist

    def verify(self, reference):

        return self.gateway.verify_payment(reference)
