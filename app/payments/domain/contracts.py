# Every payment gateway must implement this.

from abc import ABC, abstractmethod


class PaymentGateway(ABC):

    @abstractmethod
    def create_payment(self, amount, currency, reference, metadata):
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
    