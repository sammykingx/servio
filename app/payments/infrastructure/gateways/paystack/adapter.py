# Paystack gateway adapter implementing PaymentGateway contract.

from core.url_names import PaymentURLS
from django.conf import settings
from django.urls import reverse_lazy
from requests.exceptions import HTTPError, Timeout, RequestException
from payments.domain.contracts import PaymentGateway
from payments.domain.enums import RegisteredPaymentProvider
from payments.domain.entities import GatewayInitializationResultEntity
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import PaymentGatewayError
from payments.schemas.payments import PaymentGatewayRequest
from payments.schemas.paystack import PaystackInitializationResponseSchema, PaystackVerificationResponseSchema


import json, logging, requests


logger = logging.getLogger("app_file")


class PaystackAdapter(PaymentGateway):
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.callback_url = reverse_lazy(PaymentURLS.PAYMENT_VERIFICATION, kwargs={"gateway": "paystack"})
        self.timeout = (5, 17) # (Connect Timeout, Read Timeout)

        if not all([self.secret_key, self.public_key, self.callback_url]):
            raise ValueError("Paystack configuration is incomplete. Please check your environment variables.")

    @property
    def create_payment_endpoint(self) -> str:
        return f"{self.BASE_URL}/transaction/initialize"

    @property
    def verify_payment_endpoint(self) -> str:
        return f"{self.BASE_URL}/transaction/verify/{{reference}}"
    
    def _get_headers(self):
        """Helper method to construct headers for Paystack API requests."""
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
        
        return headers
    
    def create_payment(self, payload: PaymentGatewayRequest) -> GatewayInitializationResultEntity:
        data = PaymentGatewayRequest.model_dump(payload, mode='json')
        data["callback_url"] = self.callback_url
        data["metadata"] = {"cancel_action": reverse_lazy(PaymentURLS.CANCELLED_PAYMENT_CHECKOUT)}
        # data["channels"] = ["card", "bank", "apple_pay", "ussd", "qr", "mobile_money", "bank_transfer", "eft", "capitec_pay", "payattitude"]
        
        try:
            response = requests.post(
                self.create_payment_endpoint,
                headers=self._get_headers(),
                json=data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            json_data:dict = response.json()
            paystack_res = PaystackInitializationResponseSchema(**json_data)
            return GatewayInitializationResultEntity(
                gateway=RegisteredPaymentProvider.PAYSTACK,
                message=paystack_res.message,
                data=paystack_res.data
            )
        
            # Actual return object from paystack
            # data = {
            #     'status': True, 
            #     'message': 'Authorization URL created', 
            #     'data': {
            #         'authorization_url': 'https://checkout.paystack.com/u4j84p5z4jd6krf', 
            #         'access_code': 'u4j84p5z4jd6krf', 
            #         'reference': 'SRV-jSCgCj9KZ0NehGo'
            #     }
            # }
            # return data
        
        except Timeout:
            raise PaymentGatewayError(
                "Payment service timed out. Please try again later.",
                code=PaymentFailure.GATEWAY_TIMEOUT.code,
                title=PaymentFailure.GATEWAY_TIMEOUT.title,
            )

        except HTTPError as e:
            if e.response.status_code == 401:
                raise PaymentGatewayError(
                    "Invalid initialization data for gateway - paystack",
                    code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                    title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title,
                )

            # 400
            raise PaymentGatewayError(
                "Prevented a duplicate initialization to protect against double-charging.",
                code=PaymentFailure.DUPLICATE_PAYMENT_REFERENCE.code,
                title=PaymentFailure.DUPLICATE_PAYMENT_REFERENCE.title,
                err_type="warning"
            )
            
        except RequestException as err:
            logger.error(err)
            raise PaymentGatewayError(
                f"Connection error: {str(e)}",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )
        
    def verify_payment(self, reference: str):
        try:
            # try for an invalid ref
            response = requests.get(
                self.verify_payment_endpoint.format(reference=reference),
                headers=self._get_headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            json_data:dict = response.json()
            paystack_res = PaystackInitializationResponseSchema(
                message=json_data.get("message"),
                data=json_data.get("data"),
                metadata=json_data
            )
            print(response.json())
            return response.json()
        
        except Timeout:
            raise PaymentGatewayError(
                "Payment service took too long to respond during verification session. Please try again later.",
                code=PaymentFailure.GATEWAY_TIMEOUT.code,
                title=PaymentFailure.GATEWAY_TIMEOUT.title,
            )

        except HTTPError as e:
            raise PaymentGatewayError(
                "The transaction reference provided is invalid or could not be found.",
                code=PaymentFailure.INVALID_REFERENCE.code,
                title=PaymentFailure.INVALID_REFERENCE.title,
                err_type="warning"
            )
            
        except RequestException as e:
            logger.error(e)
            raise PaymentGatewayError(
                f"Connection error: {str(e)}",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )

    def refund(self, reference, amount):
        pass

    def transfer(self, recipient, amount):
        pass
    
    def charge_backs(self, reference):
        pass
    