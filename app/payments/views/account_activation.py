from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import View
from django.shortcuts import render, redirect
from core.url_names import PaymentURLS
from formatters.pydantic_formatter import format_pydantic_errors
from payments.domain.enums import PaymentStatus, PaymentType, PaymentPurpose, PaymentPhase
from payments.domain.exceptions import DomainException
from payments.infrastructure.registry import GATEWAYS
from payments.schemas.payments import ActivePaymentSession, PaymentManifest
from payments.services.payment_service import PaymentService
from template_map.payments import Payments
from pydantic import ValidationError
from decimal import Decimal
from constants import APP_SUBSCRIPTION_FEE
import json



class AccountActivationView(LoginRequiredMixin, View):
    template_name = Payments.Checkouts.PAYSTACK_CHECKOUT
    
    def get(self, request, *args, **kwargs):
        provider:str = kwargs.get("gateway")
        if provider not in GATEWAYS.keys():
            return render(request, Payments.Checkouts.UNREGISTERED_GATEWAY, context={"provider" : provider.lower()})
        amount = Decimal(str(APP_SUBSCRIPTION_FEE))
        entity = PaymentService(
            gateway_name=provider,
            phase=PaymentPhase.INITIALIZATION, 
            user=self.request.user
        ).initiate_payment(
            amount=amount,
            payment_type=PaymentType.ONE_TIME, 
            payment_purpose=PaymentPurpose.ACTIVATION_FEE
        )
        
        context = {
            "provider": entity.gateway,
            "reference": entity.reference,
            "status": entity.status,
        }
        
        if entity.status == PaymentStatus.SUCCESS:
            return redirect(reverse_lazy(PaymentURLS.CHECKOUT_COMPLETE))
        
        return render(request, self.template_name, context=context)
    
    def post(self, request, *args, **kwargs):
        try:
            payload = ActivePaymentSession(**json.loads(request.body))
            payment_service = PaymentService(
                gateway_name=payload.provider, 
                phase=PaymentPhase.INITIALIZATION, 
                user=self.request.user
            )
            resp = payment_service.process_payment(payload.reference)
            response_data = PaymentManifest(
                status=PaymentStatus.SUCCESS,
                title=resp.get("message", "Checkout URL ready"),
                message="Payment initialized successfully",
                data=resp.get("data", {}),
                ui_intent=PaymentStatus.SUCCESS
            )
            return JsonResponse(response_data.model_dump(), status=200)
            # https://checkout.paystack.com/u4j84p5z4jd6krf
            # SRV-jSCgCj9KZ0NehGo
            # try to cancell and see if it will resume again

        except json.JSONDecodeError:
            err = PaymentManifest(
                status=PaymentStatus.FAILED,
                title="Invalid JSON payload",
                message="Invalid data format",
                ui_intent="warning",
            )
            return JsonResponse(err.model_dump(), status=400)
        
        except ValidationError as e:
            fields = format_pydantic_errors(e),
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
            err = PaymentManifest(
                status=PaymentStatus.FAILED,
                title="Payment Error",
                message="An unexpected error occurred while processing your payment. Please try again later.",
                ui_intent="error",
            )
            return JsonResponse(err.model_dump(), status=500)
