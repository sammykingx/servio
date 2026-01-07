from django.apps import apps
from django.urls import reverse_lazy
from core.url_names import CollaborationURLS
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from template_map.payments import Payments
from collaboration.models.choices import GigStatus
from ..mixins import GigPaymentMixin


GigModel = apps.get_model("collaboration","Gig")


class GigPaymentSummaryView(
    LoginRequiredMixin,
    GigPaymentMixin,
    TemplateView
):
    template_name = Payments.GigPayments.GIG_OVERVIEW

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_gig_context())
        return context


class GigCardPayments(LoginRequiredMixin, GigPaymentMixin, TemplateView):
    template_name = Payments.GigPayments.CARD_PAYMENTS
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_gig_context())
        return context
    
class ProcessGigPaymentView(
    LoginRequiredMixin,
    GigPaymentMixin,
    TemplateView
):
    template_name = Payments.GigPayments.PROCESS_PAYMENT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_gig_context())
        return context

    def post(self, request, *args, **kwargs):
        """
        Receives gig payment payload (HTMX / JSON / form)
        """
        payload = request.POST  # or request.body for JSON

        # ⚠️ Do NOT trust payload amounts here
        # You will validate against server-side gig data

        # Example stub
        # payment_intent = create_or_update_intent(self.gig, payload)

        return self.render_to_response(
            self.get_context_data()
        )
