# Core orchestration logic for processing payments regradless of gateway.


from payments.infrastructure.registry import GATEWAYS
from payments.domain.enums import RegisteredPaymentProvider
from payments.domain.exceptions import DomainException, PolicyViolationError
from payments.domain.constants import PaymentFailure


class PaymentService:

    def __init__(self, gateway_name: RegisteredPaymentProvider):
        try:
            provider = RegisteredPaymentProvider(gateway_name)
            if provider not in GATEWAYS:
                raise DomainException(
                    f"Gateway '{provider}' is registered but has no Adapter.",
                    code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                    title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title
                )

            gateway_class = GATEWAYS[provider]
            self.gateway = gateway_class()
            self.charge_url
            
        except ValueError:
            raise DomainException(
                f"'{gateway_name.title()}' is not a supported payment provider.", 
                code=PaymentFailure.UNSUPPORTED_PROVIDER.code, 
                title=PaymentFailure.UNSUPPORTED_PROVIDER.title
            )

    def charge(self, amount, currency, reference, metadata):
        """Orchestrates the payment creation process."""

        return self.gateway.create_payment(
            amount,
            currency,
            reference,
            metadata
        )
        # create customer if they don't exist

    def verify(self, reference):

        return self.gateway.verify_payment(reference)
