from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from core.url_names import ContractURLS, PaymentURLS
from formatters.pydantic_formatter import format_pydantic_errors
from payments.domain.enums import PaymentPhase, PaymentPurpose, PaymentStatus
from payments.domain.entities.gateway import GatewayVerifyResponse as GatewayResult
from payments.domain.entities.payments import PaymentEntity
from payments.domain.exceptions import DomainException
from payments.schemas.payments import ActivePaymentSession, PaymentManifest
from payments.infrastructure.registry import GATEWAYS
from payments.services.payment_service import PaymentService
from template_map.payments import Payments
from pydantic import ValidationError
from typing import Tuple, Union
import json, logging


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentVerificationView(View):
    template_name = Payments.Checkouts.PAYMENT_VERIFICATION
    # https://checkout.paystack.com/330vassuf3todt3
    # http://localhost:8000/payments/checkout/paystack/verify/?reference=SRV-jSCgCj9KZ0NehGo
    
    def get(self, request, *args, **kwargs):
        provider:str = kwargs.get("gateway")
        reference:str = request.GET.get("reference")
        if provider not in GATEWAYS.keys():
            return render(request, Payments.Checkouts.UNREGISTERED_GATEWAY, context={"provider" : provider.lower()})
        context = {
            "provider": provider,
            "reference": reference,
            "verificationUrl": reverse(PaymentURLS.PAYMENT_VERIFICATION, kwargs={"gateway": provider})
        }
        return render(request, self.template_name, context=context)
    
    def post(self, request, *args, **kwargs):
        try:
            payload = ActivePaymentSession.model_validate_json(request.body)
            result, payment = PaymentService(
                request=request,
                gateway_name=payload.provider, 
                phase=PaymentPhase.VERIFICATION
            ).verify(payload.reference)
        
            redirect, url = self._should_redirect(payment)
            
            resp = PaymentManifest(
                status=result.data.status,
                title="Veficicatipn Complete 🎉!",
                message=result.message.title(),
                data={"paid_at": result.data.paid_at, "reference": payload.reference},
                ui_intent="success",
                redirect=redirect,
                url=url
            )
            return JsonResponse(resp.model_dump(mode="json"), status=200)
            
        except ValidationError as e:
            fields = format_pydantic_errors(e),
            print(fields)
            err = PaymentManifest(
                status=PaymentStatus.FAILED,
                title="Validation error",
                message="Some required information is missing or invalid.",
                ui_intent="warning",
            )
            return JsonResponse(err.model_dump(), status=400)
                
        except DomainException as e:
            err = PaymentManifest(
                status=PaymentStatus.FAILED,
                title=e.title,
                message=e.message,
                ui_intent=e.err_type,
            )
            return JsonResponse(err.model_dump(), status=400)
        
        except Exception as e:
            logger.exception(e)
            err = PaymentManifest(
                status=PaymentStatus.FAILED,
                title="Payment Verification Incomplete",
                message="An unexpected error occurred while verifying your payment. Please try again later.",
                ui_intent="error",
            )
            return JsonResponse(err.model_dump(), status=500)
        
    def _should_redirect(self, payment: PaymentEntity) -> Tuple[bool, Union[str, None]]:
        if payment.payment_purpose == PaymentPurpose.CONTRACT_ACTIVATION:
            if not payment.contract_ref:
                return False, None
                
            url = reverse(
                ContractURLS.ACTIVATE_CONTRACT, 
                kwargs={"contract_ref": payment.contract_ref}
            )
            return True, url
        
        return False, None
