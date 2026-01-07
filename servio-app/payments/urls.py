from django.urls import path, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from core.url_names import PaymentURLS
from template_map.payments import Payments
from .views.gig_payments import GigPaymentSummaryView, ProcessGigPaymentView, GigCardPayments


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
        GigPaymentSummaryView.as_view(),
        name=PaymentURLS.GIG_PAYMENT_SUMMARY
    ),
    path(
        "gig-payments/<uuid:gig_id>/pay", 
        ProcessGigPaymentView.as_view(),
        name=PaymentURLS.PROCESS_GIG_PAYMENT
    ),
    path(
        "gig-payments/<uuid:gig_id>/pay/card", 
        GigCardPayments.as_view(),
        name=PaymentURLS.GIG_CARD_PAYMENT
    )
]