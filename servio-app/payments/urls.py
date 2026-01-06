from django.urls import path, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from core.url_names import PaymentURLS
from template_map.payments import Payments
from template_map.collaboration import Collabs
from .views.gig_payments import GigPaymentView


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(PaymentURLS.USER_PAYMENT_SUMMARY), permanent=True
        ),
    ),
    path(
        "all-payments/", 
         TemplateView.as_view(template_name=Payments.SUMMARY), 
         name=PaymentURLS.USER_PAYMENT_SUMMARY
    ),
    path(
        "gig-payments/<uuid:gig_id>", 
        GigPaymentView.as_view(),
        name=PaymentURLS.GIG_PAYMENT_SUMMARY
    )
]