# Paystack gateway adapter implementing PaymentGateway contract.

from payments.domain.contracts import PaymentGateway
from decouple import config
import paystack, requests


class PaystackAdapter(PaymentGateway):
    create_payment_endpoint = "https://api.paystack.co/transaction/initialize"
    verify_payment_endpoint = "https://api.paystack.co/transaction/verify/{reference}"

    def __init__(self):
        self.secret_key = config("PAYSTACK_TEST_SECRET_KEY") if config("ENVIRONMENT") == "development" else config("PAYSTACK_LIVE_SECRET_KEY")
        self.public_key = config("PAYSTACK_TEST_PUBLIC_KEY") if config("ENVIRONMENT") == "development" else config("PAYSTACK_LIVE_PUBLIC_KEY")
        self.callback_url = config("PAYSTACK_CALLBACK_URL")
        paystack.api_key = self.secret_key

        if not all([self.secret_key, self.public_key, self.callback_url]):
            raise ValueError("Paystack configuration is incomplete. Please check your environment variables.")

    def create_payment(self, amount, currency, reference, metadata):

        # response = requests.post(
        #     self.create_payment_endpoint,
        #     headers={"Authorization": f"Bearer {self.secret_key}"},
        #     json={
        #         "amount": amount,
        #         "reference": reference,
        #         "metadata": metadata,
        #         "currency": currency
        #     },
        # )
        # create(
            # email=email, amount=amount, 
            # authorization_code=authorization_code, 
            # pin=pin, reference=reference, 
            # birthday=birthday, 
            # device_id=device_id, 
            # metadata=metadata, 
            # bank=bank, mobile_money=mobile_money, 
            # ussd=ussd, eft=eft
        # )
        response = paystack.Charge.create(
            email=metadata.get("email"),
            authorization_code=self.public_key,
            amount=amount,
            reference=reference,
            metadata=metadata
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