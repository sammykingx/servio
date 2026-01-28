from django.apps import apps
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Prefetch
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.address import AddressType
from collaboration.models.choices import GigStatus, PaymentOption
from collaboration.schemas.gig_role import PAYMENT_OPTIONS
from core.url_names import OppurtunitiesURLS
from template_map.collaboration import Collabs
import json


GigModel = apps.get_model("collaboration","Gig")
GigRoleModel = apps.get_model("collaboration", "GigRole")
GigApplicationModel = apps.get_model("collaboration", "GigApplication")

class AcceptOppurtuniyDetailView(LoginRequiredMixin, DetailView):
    model = GigModel
    template_name = Collabs.Oppurtunities.ACCEPT_OFFER
    context_object_name = "gig"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        return super().get_queryset().filter(
            status=GigStatus.PUBLISHED
        ).exclude(creator=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(OppurtunitiesURLS.ALL))
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["payment_options"] = json.dumps(PAYMENT_OPTIONS)
        context["negotiating"] = True if self.request.GET.get("negotiating") == "true" else False
        roles = self.object.required_roles.all()
        role_payment_meta = {}
        if roles:
            for role in roles:
                payment_value = role.payment_option

                is_split = PaymentOption.is_split(payment_value)

                role_payment_meta[role.id] = {
                    "type": "Percentage Split" if is_split else "Full Upfront",
                    "installments": (
                        PaymentOption.installments_count(payment_value)
                        if is_split
                        else 1
                    ),
                    "split": (
                        PaymentOption.percentages(payment_value)
                        if is_split
                        else [100]
                    ),
                    "label": PaymentOption(payment_value).label,
                }
                
            context["role_payment_meta"] = role_payment_meta
        return context