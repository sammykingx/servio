from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import View
from django.shortcuts import render, redirect
from core.url_names import AuthURLNames,PaymentURLS
from formatters.pydantic_formatter import format_pydantic_errors
from payments.domain.enums import RegisteredPaymentProvider, PaymentStatus
from payments.domain.exceptions import DomainException
from payments.infrastructure.registry import GATEWAYS
from payments.schemas.paystack import InitializePaymentPayload, PaystackInitializeAPIResponse
from payments.services.payment_service import PaymentService
from template_map.payments import Payments
from pydantic import ValidationError
import json



class AccountActivationView(LoginRequiredMixin, View):
    template_name = Payments.Checkouts.SUBSCRIPTION_CHECKOUT
    
    def get(self, request, *args, **kwargs):
        provider = kwargs.get("gateway")
        if provider not in GATEWAYS.keys():
            return render(request, Payments.Checkouts.UNREGISTERED_GATEWAY, context={"provider" : provider.lower()})
        
        payment_obj = PaymentService(provider, self.request.user).get_or_initiate_activation_payment()
        context = {
            "provider": payment_obj.gateway,
            "reference": payment_obj.reference,
            "status": payment_obj.status,
        }
        
        if payment_obj.status == PaymentStatus.SUCCESS:
            return redirect(reverse_lazy(PaymentURLS.CHECKOUT_COMPLETE, kwargs=context))
        
        return render(request, self.template_name, context=context)
    
    def post(self, request, *args, **kwargs):
        try:
            payload = InitializePaymentPayload(**json.loads(request.body))
            payment_service = PaymentService(payload.provider, self.request.user)
            resp = payment_service.process_one_time_payment(payload.reference)
            print("json last")
            if payload.provider == RegisteredPaymentProvider.PAYSTACK:
                response_data = PaystackInitializeAPIResponse(
                    status=resp.get("status", True),
                    title=resp.get("messge", "Checkout URL ready"),
                    message="Payment initialized successfully",
                    data=resp.get("data", {})
                )
                return JsonResponse(response_data.model_dump(), status=200)
                # https://checkout.paystack.com/u4j84p5z4jd6krf
                # SRV-jSCgCj9KZ0NehGo
                # try to cancell and see if it will resume again

        except json.JSONDecodeError:
            err = PaystackInitializeAPIResponse(
                status=False,
                title="Invalid JSON payload",
                message="Invalid data format",
                response_type="warning",
            )
            return JsonResponse(err.model_dump(), status=400)
        
        except ValidationError as e:
            fields = format_pydantic_errors(e),
            print(fields)
            err = PaystackInitializeAPIResponse(
                status=False,
                title="Validation error",
                message="Some required information is missing or invalid.",
                response_type="warning",
            )
            return JsonResponse(err.model_dump(), status=400)
                
        except DomainException as e:
            err = PaystackInitializeAPIResponse(
                status=False,
                title=e.title,
                message=e.message,
                response_type=e.err_type,
            )
            return JsonResponse(err.model_dump(), status=400)
        
        except Exception as e:
            print(f"Unexpected error during payment processing: {str(e)}")
            err = PaystackInitializeAPIResponse(
                status=False,
                title="Payment Error",
                message="An unexpected error occurred while processing your payment. Please try again later.",
                response_type="error",
            )
            return JsonResponse(err.model_dump(), status=500)
