# Paystack gateway adapter implementing PaymentGateway contract.

from django.urls import reverse_lazy
from payments.domain.contracts import PaymentGateway
from payments.schemas.payments import PaymentRequest
from payments.domain.exceptions import PaymentGatewayError
from payments.domain.errors import PaymentFailure
from core.url_names import PaymentURLS
from decouple import config
from requests.exceptions import Timeout, RequestException
import json, requests


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
        data = PaymentRequest.model_dump(payload)
        data["callback_url"] = self.callback_url
        data["metadata"] = {"cancel_action": reverse_lazy(PaymentURLS.CANCELLED_PAYMENT_CHECKOUT)}
        # data["channels"] = ["card", "bank", "apple_pay", "ussd", "qr", "mobile_money", "bank_transfer", "eft", "capitec_pay", "payattitude"]
        
        try:
            response = requests.post(
                self.create_payment_endpoint,
                headers=self._get_headers(),
                json=json.loads(json.dumps(data, default=str)),
                timeout=(5, 13),
            )
            response.raise_for_status()
            return response.json()
        
        except Timeout:
            raise PaymentGatewayError(
                "Payment service timed out. Please try again later.",
                code=PaymentFailure.GATEWAY_TIMEOUT.code,
                title=PaymentFailure.GATEWAY_TIMEOUT.title,
                type="warning"
            )
        
        except RequestException as e:
            raise PaymentGatewayError(
                f"Connection error: {str(e)}",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                type="error"
            )
        # {
            # 'status': True, 
            # 'message': 'Authorization URL created', 
            # 'data': {
                # 'authorization_url': 'https://checkout.paystack.com/cirt0f31hcl7seo', 
                # 'access_code': 'cirt0f31hcl7seo', 
                # 'reference': 'SRV-ChkiHvUa0WrbWlY'
                # }
            # }

    def verify_payment(self, reference):

        response = requests.get(
            self.verify_payment_endpoint.format(reference=reference),
            headers=self._get_headers(),
        )

        return response.json()

    def refund(self, reference, amount):
        pass

    def transfer(self, recipient, amount):
        pass
    