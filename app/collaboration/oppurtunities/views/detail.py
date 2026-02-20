from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.address import AddressType
from collaboration.models.choices import GigStatus, PaymentOption
from core.url_names import OppurtunitiesURLS
from template_map.collaboration import Collabs
from registry_utils import get_registered_model


GigModel = get_registered_model("collaboration","Gig")
GigRoleModel = get_registered_model("collaboration", "GigRole")
ProposalModel = get_registered_model("collaboration", "Proposal")

class OppurtuniyDetailView(LoginRequiredMixin, DetailView):
    model = GigModel
    template_name = Collabs.Oppurtunities.DETAIL
    context_object_name = "gig"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        return super().get_queryset().filter(
            status__in=[
                GigStatus.PUBLISHED,
                GigStatus.IN_PROGRESS,
                GigStatus.COMPLETED,
                GigStatus.CANCELLED,
            ]
        )
        
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(OppurtunitiesURLS.ALL))

    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["creator_location"] = self.object.creator.addresses.filter(label=AddressType.HOME).first()
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