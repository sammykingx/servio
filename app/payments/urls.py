from django.urls import path, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, RedirectView
from core.url_names import PaymentURLS
from template_map.payments import Payments
from .views.gig_payments import GigPaymentSummaryView, ProcessGigPaymentView, SelectGigPaymentMethodView, GigCardInfoView, GigPaymentComplete
from .views.account_activation import AccountActivationView
from .views.webhooks import PaystackWebhookView
from .views.verification import PaymentVerificationView
from .views.listings import UserPaymentsListView


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(PaymentURLS.USER_PAYMENT_SUMMARY), permanent=True
        ),
    ),
    path(
        "user-subscription/", 
        login_required(TemplateView.as_view(template_name=Payments.ANNUAL_SUBSCRIPTION)),
        name=PaymentURLS.PAY_SUBSCRIPTION
    ),
    path(
        "user-subscription/confirm-currency/", 
        TemplateView.as_view(template_name=Payments.Checkouts.SUBSCRIPTION_CHECKOUT_CURRENCY),
        name=PaymentURLS.SUBSCRIPTION_CHECKOUT_OPTION
    ),
    path(
        "user-subscription/checkout/<str:gateway>/",
        AccountActivationView.as_view(),
        name=PaymentURLS.SUBSCRIPTION_CHECKOUT,
    ),
    path(
        "checkout/<str:gateway>/verify/",
        PaymentVerificationView.as_view(),
        name=PaymentURLS.PAYMENT_VERIFICATION,
    ),
    path(
        "checkout/cancelled/",
        TemplateView.as_view(template_name=Payments.Checkouts.CHECKOUT_CANCELLED),
        name=PaymentURLS.CANCELLED_PAYMENT_CHECKOUT,
    ),
    path(
        "checkout/complete/",
        TemplateView.as_view(template_name=Payments.Checkouts.CHECKOUT_COMPLETE),
        name=PaymentURLS.CHECKOUT_COMPLETE,
    ),
    path(
        "summary/", 
        UserPaymentsListView.as_view(), 
        name=PaymentURLS.USER_PAYMENT_SUMMARY
    ),
    
    # WEBHOOKS URLS
    path(
        "webhook/paystack/", 
        PaystackWebhookView.as_view(), 
        name=PaymentURLS.PAYSTACK_WEBHOOK,
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
