# Paystack gateway adapter implementing PaymentGateway contract.

from core.url_names import PaymentURLS
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from requests.exceptions import HTTPError, Timeout, RequestException
from payments.domain.contracts import PaymentGateway
from payments.domain.enums import RegisteredPaymentProvider
from payments.domain.entities.gateway import GatewayInitResponse, GatewayVerifyResponse
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import PaymentGatewayError
from payments.schemas.payments import PaymentGatewayPayload
from payments.schemas.paystack import PaystackInitResponseSchema, PaystackVerificationData
import logging, requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PaystackAdapter(PaymentGateway):
    BASE_URL = "https://api.paystack.co"

    def __init__(self, request: HttpRequest):
        self.request = request
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.callback_url = request.build_absolute_uri(
            reverse(PaymentURLS.PAYMENT_VERIFICATION, kwargs={"gateway": "paystack"})
        )
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
    
    def create_payment(self, payload: PaymentGatewayPayload) -> GatewayInitResponse:
        data = payload.model_dump(mode="json")
        data["callback_url"] = self.callback_url
        data["metadata"] = {"cancel_action": reverse(PaymentURLS.CANCELLED_PAYMENT_CHECKOUT)}
        
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
            paystack_res = PaystackInitResponseSchema(**json_data)
            return GatewayInitResponse(
                gateway=RegisteredPaymentProvider.PAYSTACK,
                message=paystack_res.message,
                data=paystack_res.data
            )
        
            # Actual return object from paystack
            # {
            #   'status': True, 
            #   'message': 'Authorization URL created', 
            #   'data': {
            #      'authorization_url': 'https://checkout.paystack.com/u4j84p5z4jd6krf', 
            #      'access_code': 'u4j84p5z4jd6krf', 
            #      'reference': 'SRV-jSCgCj9KZ0NehGo'
            #   }
            # }
        
        except Timeout:
            raise PaymentGatewayError(
                "Payment service timed out. Please try again later.",
                code=PaymentFailure.GATEWAY_TIMEOUT.code,
                title=PaymentFailure.GATEWAY_TIMEOUT.title,
            )

        except HTTPError as e:
            err:dict = e.response.json()
            logger.exception(err)
            if e.response.status_code == 401:
                raise PaymentGatewayError(
                    "Invalid initialization data for gateway - paystack",
                    code=PaymentFailure.PROVIDER_NOT_CONFIGURED.code,
                    title=PaymentFailure.PROVIDER_NOT_CONFIGURED.title,
                )

            # 400
            if err.get("code") == "amount_exceed_limit":
                raise PaymentGatewayError(
                  "This amount is over the maximum payment limit",
                  code=PaymentFailure.AMOUNT_LIMIT_EXCEEDED.code,
                  title=PaymentFailure.AMOUNT_LIMIT_EXCEEDED.title,
                  err_type="warning",
                )
                
            raise PaymentGatewayError(
                "We were unable to initialize your payment. Please try again or contact support.",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title="Paystack Nigeria",
                err_type="warning"
            )
            
        except RequestException as err:
            logger.exception(err)
            raise PaymentGatewayError(
                f"Connection error: {str(e)}",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )
        
    def verify_payment(self, reference: str) -> GatewayVerifyResponse:
        """
        Queries Paystack to confirm the final status of a transaction.
        """
        try:
            response = requests.get(
                self.verify_payment_endpoint.format(reference=reference),
                headers=self._get_headers(),
                timeout=self.timeout,
            )
            
            response.raise_for_status()
            resp_data:dict = response.json()
            data:dict = resp_data.get("data", {})
            status:str = data.get("status")
            is_successful = status == "success"
            
            paystack_res = PaystackVerificationData(
                paystack_metadata=resp_data,
                **data,
            )
            gw_entity = GatewayVerifyResponse(
                gateway=RegisteredPaymentProvider.PAYSTACK,
                status=status,
                message=data.get("gateway_response"),
                was_successful=is_successful,
                data=paystack_res,
            )
            return gw_entity
        
        except Timeout:
            raise PaymentGatewayError(
                "Payment service took too long to respond during verification session. Please refresh or try again later.",
                code=PaymentFailure.GATEWAY_TIMEOUT.code,
                title=PaymentFailure.GATEWAY_TIMEOUT.title,
            )

        except HTTPError:
            raise PaymentGatewayError(
                "The transaction reference provided is invalid or could not be found.",
                code=PaymentFailure.INVALID_REFERENCE.code,
                title=PaymentFailure.INVALID_REFERENCE.title,
                err_type="warning"
            )
            
        except RequestException as e:
            logger.exception(e)
            raise PaymentGatewayError(
                f"Connection error: {str(e)}",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )

    def refund(self, reference, amount):
        pass

    def charge_backs(self, reference):
        pass
    
    def get_ngn_banks(self) -> List[Dict[str, Any]]:
        """Fetches a list of Nigerian banks from the API."""
        query_params = {
            "country": "nigeria",
            # "use_cursor": "true",
            # "perPage": 70,
        }
        url = f"{self.BASE_URL}/bank"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=query_params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            json_data:dict = response.json()
            return json_data.get("data", [])
        
        except Timeout:
            raise PaymentGatewayError(
                "Payment service timed out while fetching bank list. Please try again later.",
                code=PaymentFailure.GATEWAY_TIMEOUT.code,
                title=PaymentFailure.GATEWAY_TIMEOUT.title,
            )

        except HTTPError as e:
            logger.exception(e)
            raise PaymentGatewayError(
                "Failed to retrieve bank list from payment provider.",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )
            
        except RequestException as e:
            logger.exception(e)
            raise PaymentGatewayError(
                f"Connection error: {str(e)}",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )
            
    def resolve_account_number(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/bank/resolve"
        query_params = {
            "account_number": account_number,
            "bank_code": bank_code,
        }
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=query_params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            json_data:dict = response.json()
            # {'status': True, 'message': 'Account number resolved', 'data': {'account_number': '1234567890', 'account_name': 'John Doe', 'bank_id': 234}}
            return json_data
        
        except Timeout:
            raise PaymentGatewayError(
                "Payment service timed out while resolving account details. Please try again later.",
                code=PaymentFailure.GATEWAY_TIMEOUT.code,
                title=PaymentFailure.GATEWAY_TIMEOUT.title,
            )

        except HTTPError as e:
            logger.exception(e)
            raise PaymentGatewayError(
                "Failed to resolve account details with payment provider.",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )
            
        except RequestException as e:
            logger.exception(e)
            raise PaymentGatewayError(
                f"Connection error: {str(e)}",
                code=PaymentFailure.GATEWAY_ERROR.code,
                title=PaymentFailure.GATEWAY_ERROR.title,
                err_type="error"
            )
    