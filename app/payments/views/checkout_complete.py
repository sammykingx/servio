from django.views.generic import TemplateView
from template_map.payments import Payments
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import DomainException, PolicyViolationError
from registry_utils import get_registered_model

PaymenttModel = get_registered_model("payments", "Payment")

class CheckoutCompleteView(TemplateView):
    template_name = Payments.Checkouts.PAYMENT_RESULT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reference = self.request.GET.get(reference)
        provider = self.request.GET.get(provider)

        context['status'] = "failed"
        context["amount"] = "$30.00"
        context["reference"] = "SERRV-wsdhfjtu7ivh"
        # http 404 for invalid refor gateway
        # add the user that paid, the amount add others
        # with paid stamp
        return context
    
    def get_record(self, txref, provider):
        payment_obj = PaymenttModel.objects.filter(
            reference=txref, gateway=provider
        ).first()
        if not payment_obj:
            raise PolicyViolationError(
                message="We couldn't find a record for this payment. Please check your reference number or try again.",
                code=PaymentFailure.INVALID_REFERENCE.code,
                title=PaymentFailure.INVALID_REFERENCE.title,
            )
        return payment_obj