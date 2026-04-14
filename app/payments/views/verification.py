from django.shortcuts import render
from django.views.generic import View
from payments.infrastructure.registry import GATEWAYS
from payments.services.payment_service import PaymentService
from template_map.payments import Payments


class PaymentVerificationView(View):
    template_name = Payments.Checkouts.PAYMENT_VERIFICATION
    
    def get(self, request, *args, **kwargs):
        provider = kwargs.get("gateway")
        reference = request.GET.get("txref")
        if provider not in GATEWAYS.keys():
            return render(request, Payments.Checkouts.UNREGISTERED_GATEWAY, context={"provider" : provider.lower()})
        # response = PaymentService(provider, self.request.user).verify(reference)
        context = {
            "provider": provider,
            "reference": "SRV-234dhfbvi0jd",
        }
        return render(request, self.template_name, context=context)