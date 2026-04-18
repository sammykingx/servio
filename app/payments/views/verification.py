from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from core.url_names import PaymentURLS
from formatters.pydantic_formatter import format_pydantic_errors
from payments.domain.enums import PaymentPhase
from payments.domain.entities.gateway import GatewayVerifyResponse as GatewayResult
from payments.domain.exceptions import DomainException
from payments.schemas.payments import ActivePaymentSession, PaymentManifest
from payments.infrastructure.registry import GATEWAYS
from payments.services.payment_service import PaymentService
from template_map.payments import Payments
from pydantic import ValidationError
import json


@method_decorator(csrf_exempt, name='dispatch')
class PaymentVerificationView(View):
    template_name = Payments.Checkouts.PAYMENT_VERIFICATION
    # http://localhost:8000/payments/checkout/paystack/verify/?trxref=SRV-jSCgCj9KZ0NehGo
    
    def get(self, request, *args, **kwargs):
        provider:str = kwargs.get("gateway")
        reference:str = request.GET.get("trxref")
        if provider not in GATEWAYS.keys():
            return render(request, Payments.Checkouts.UNREGISTERED_GATEWAY, context={"provider" : provider.lower()})
        context = {
            "provider": provider,
            "reference": reference,
            "verificationUrl": reverse_lazy(PaymentURLS.PAYMENT_VERIFICATION, kwargs={"gateway": provider})
        }
        return render(request, self.template_name, context=context)
    
    def post(self, request, *args, **kwargs):
        try:
            payload = ActivePaymentSession(**json.loads(request.body))
            result:GatewayResult = PaymentService(
                gateway_name=payload.provider, 
                phase=PaymentPhase.VERIFICATION
            ).verify(payload.reference)
            # return HttpResponse(status=200)
        
            resp = PaymentManifest(
                status=result.data.status,
                title=result.message.title(),
                message="We’ve received your payment. You're all set to go 🎉!",
                data={"paid_at": result.data.paid_at, "reference": payload.reference},
                ui_intent="success",
            )
            return JsonResponse(resp.model_dump(), status=200)
            
        except json.JSONDecodeError:
            err = PaymentManifest(
                status="failed",
                title="Invalid JSON payload",
                message="Invalid data format",
                ui_intent="warning",
            )
            return JsonResponse(err.model_dump(), status=400)
        
        except ValidationError as e:
            fields = format_pydantic_errors(e),
            print(fields)
            err = PaymentManifest(
                status="failed",
                title="Validation error",
                message="Some required information is missing or invalid.",
                ui_intent="warning",
            )
            return JsonResponse(err.model_dump(), status=400)
                
        except DomainException as e:
            err = PaymentManifest(
                status="failed",
                title=e.title,
                message=e.message,
                ui_intent=e.err_type,
            )
            return JsonResponse(err.model_dump(), status=400)
        
        except Exception as e:
            print(e)
            err = PaymentManifest(
                status="failed",
                title="Payment Verification Incomplete",
                message="An unexpected error occurred while verifying your payment. Please try again later.",
                ui_intent="error",
            )
            return JsonResponse(err.model_dump(), status=500)