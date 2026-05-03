# Every payment gateway must implement this.

from abc import ABC, abstractmethod
from payments.schemas.payments import PaymentGatewayPayload
from payments.domain.entities.gateway import GatewayInitResponse, GatewayVerifyResponse


class PaymentGateway(ABC):

    @abstractmethod
    def create_payment(self, payload:PaymentGatewayPayload) -> GatewayInitResponse:
        pass

    @abstractmethod
    def verify_payment(self, reference) -> GatewayVerifyResponse:
        pass

    @abstractmethod
    def refund(self, reference, amount):
        pass
    