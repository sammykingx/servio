from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from core.url_names import PaymentURLS
from formatters.pydantic_formatter import format_pydantic_errors
from payments.domain.enums import PaymentPhase
from payments.domain.exceptions import DomainException
from payments.schemas.payments import ActivePaymentSession
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
            resp = PaymentService(
                gateway_name=payload.provider, 
                phase=PaymentPhase.VERIFICATION
            ).verify(payload.reference)
            return JsonResponse(resp, status=200)
            
            
        except json.JSONDecodeError:
            # err = PaystackInitializeAPIResponse(
            #     status=False,
            #     title="Invalid JSON payload",
            #     message="Invalid data format",
            #     response_type="warning",
            # )
            return JsonResponse(payload.model_dump(), status=400)
        
        except ValidationError as e:
            fields = format_pydantic_errors(e),
            print(fields)
            # err = PaystackInitializeAPIResponse(
            #     status=False,
            #     title="Validation error",
            #     message="Some required information is missing or invalid.",
            #     response_type="warning",
            # )
            return JsonResponse(payload.model_dump(), status=400)
                
        except DomainException as e:
            # err = PaystackInitializeAPIResponse(
            #     status=False,
            #     title=e.title,
            #     message=e.message,
            #     response_type=e.err_type,
            # )
            return JsonResponse(payload.model_dump(), status=400)
        
        except Exception as e:
            print(f"Unexpected error during payment processing: {str(e)}")
            # err = PaystackInitializeAPIResponse(
            #     status=False,
            #     title="Payment Error",
            #     message="An unexpected error occurred while processing your payment. Please try again later.",
            #     response_type="error",
            # )
            return JsonResponse(payload.model_dump(), status=500)