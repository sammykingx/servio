# Stripe gateway adapter implementing PaymentGateway contract.
from payments.domain.contracts import PaymentGateway


class StripeAdapter(PaymentGateway):
    def create_payment(self, amount, currency, reference, metadata):
        pass
    
    def verify_payment(self, reference):
        pass
    
    def refund(self, reference, amount):
        pass
    
    def transfer(self, recipient, amount):
        pass
    
    