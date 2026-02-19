from django.urls import include, path, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from core.url_names import PaymentURLS
from template_map.payments import Payments
from .escrow import urls as escrow_urls
from .views.gig_payments import GigPaymentSummaryView, ProcessGigPaymentView, SelectGigPaymentMethodView, GigCardInfoView, GigPaymentComplete


urlpatterns = [
    path("escrow/", include(escrow_urls)),
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(PaymentURLS.USER_PAYMENT_SUMMARY), permanent=True
        ),
    ),
    path(
        "user-subcription/", 
         TemplateView.as_view(template_name=Payments.SUBSCRIPTION), 
         name=PaymentURLS.PAY_SUBSCRIPTION
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
        "gig-payments/<uuid:gig_id>/options", 
        SelectGigPaymentMethodView.as_view(),
        name=PaymentURLS.SELECT_GIG_PAYMENT_METHOD
    ),
    path(
        "gig-payments/<uuid:gig_id>/card", 
        GigCardInfoView.as_view(),
        name=PaymentURLS.GIG_CARD_PAYMENT
    ),
    path(
        "gig-payments/<uuid:gig_id>/checkout", 
        ProcessGigPaymentView.as_view(),
        name=PaymentURLS.GIG_PAYMENT_RESPONSE
    ),
    path(
        "gig-payments/<uuid:gig_id>/complete", 
        GigPaymentComplete.as_view(),
        name=PaymentURLS.GIG_PAYMENT_COMPLETE
    )
]