from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import View
from django.shortcuts import redirect, render
from core.url_names import AuthURLNames,PaymentURLS
from payments.services.payment_service import PaymentService
from payments.domain.enums import RegisteredPaymentProvider
from payments.domain.exceptions import DomainException
from payments.schemas.payments import PaymentRequest
from template_map.payments import Payments
from payments.infrastructure.gateways.paystack.adapter import PaystackAdapter
from constants import USD_TO_NGN_RATE



class AccountActivationView(LoginRequiredMixin, View):
    template_name = Payments.Checkouts.SUBSCRIPTION_CHECKOUT
    
    def get(self, request, *args, **kwargs):
        try:
            provider = kwargs.get("gateway")
            payment_service = PaymentService(provider, self.request.user)
            resp = payment_service.process_one_time_payment()
            if provider == RegisteredPaymentProvider.PAYSTACK.value:
                checkout_url = resp["data"]["authorization_url"]
                return redirect(checkout_url)

        except DomainException as e:
            print(e)
            # Handle domain exceptions gracefully
            toast = {
                "toast": {
                "message": e.message,
                "code": e.code,
                "title": e.title,
                "type": e.type or "error"
                }
            }
            return render(request, self.template_name, context=toast)
        
        except Exception as e:
            # Handle unexpected exceptions
            print(f"Unexpected error during payment processing: {str(e)}")
            toast = {
                "toast": {
                "message": "An unexpected error occurred while processing your payment. Please try again later.",
                "code": "unexpected_error",
                "title": "Payment Error",
                "type": "error"
                }
            }
            return render(request, self.template_name, context=toast)
        # payment service intiailize the getway based 
        # on the users location and currency default to usd
        print("succes")
        
        return render(request, self.template_name)
    
    # def post(self, request, *args, **kwargs):
    #     pass
    
    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect(reverse_lazy(AuthURLNames.LOGIN))
    #     return super().dispatch(self, request,)
    
    # def amount_in_minor_units(self, amount, gateway: str):
    #     """Converts a decimal amount to minor units based on the currency."""
    #     if gateway == RegisteredPaymentProvider.PAYSTACK.value:
    #         ngn_amount = amount * USD_TO_NGN_RATE
    #         return int(ngn_amount * 100)
    #     return int(amount * 100)
            