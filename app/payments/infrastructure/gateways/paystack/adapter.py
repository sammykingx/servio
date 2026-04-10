# Paystack gateway adapter implementing PaymentGateway contract.

from payments.domain.contracts import PaymentGateway
from payments.schemas.payments import PaymentRequest
from decouple import config
import requests


class PaystackAdapter(PaymentGateway):
    create_payment_endpoint = "https://api.paystack.co/transaction/initialize"
    verify_payment_endpoint = "https://api.paystack.co/transaction/verify/{reference}"

    def __init__(self):
        self.secret_key = config("PAYSTACK_TEST_SECRET_KEY") if config("ENVIRONMENT") == "development" else config("PAYSTACK_LIVE_SECRET_KEY")
        self.public_key = config("PAYSTACK_TEST_PUBLIC_KEY") if config("ENVIRONMENT") == "development" else config("PAYSTACK_LIVE_PUBLIC_KEY")
        self.callback_url = config("PAYSTACK_CALLBACK_URL")

        if not all([self.secret_key, self.public_key, self.callback_url]):
            raise ValueError("Paystack configuration is incomplete. Please check your environment variables.")

    def _get_headers(self):
        """Helper method to construct headers for Paystack API requests."""
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
        
        return headers
    
    def create_payment(self, payload: PaymentRequest):

        response = requests.post(
            self.create_payment_endpoint,
            headers=self._get_headers(),
            json={
                "amount": payload.amount,
                "reference": payload.reference,
                "metadata": payload.metadata,
                "currency": payload.currency
            },
        )
       

        return response.json()

    def verify_payment(self, reference):

        response = requests.get(
            self.verify_payment_endpoint.format(reference=reference),
            headers={"Authorization": f"Bearer {self.secret_key}"}
        )

        return response.json()

    def refund(self, reference, amount):
        pass

    def transfer(self, recipient, amount):
        pass
    