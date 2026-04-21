# Every payment gateway must implement this.

from abc import ABC, abstractmethod
from payments.schemas.payments import PaymentGatewayPayload


class PaymentGateway(ABC):

    @abstractmethod
    def create_payment(self, payload:PaymentGatewayPayload):
        pass

    @abstractmethod
    def verify_payment(self, reference):
        pass

    @abstractmethod
    def refund(self, reference, amount):
        pass

    @abstractmethod
    def transfer(self, recipient, amount):
        pass
    