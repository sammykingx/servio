from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.db.models import Prefetch, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from core.model_registry import registry
from core.url_names import AuthURLNames
from template_map.contracts import Contract as ContractTemplates


class RenderProposalRoleContractView(LoginRequiredMixin, DetailView):
    model = registry.Contract
    template_name = ContractTemplates.VIEW_CONTRACT
    context_object_name = "contract"
    pk_url_kwarg = "slug"
    
    def dispatch(Self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))
        
    def get_queryset(self):
        ProposalDeliverable = registry.ProposalDeliverable
        qs = (
            super().get_queryset()
            .select_related(
                "proposal_role", "project", 
                "provider", "provider__profile"
            )
            .only(
                "agreed_amount", "currency", "payment_plan", "status", "signed_at", "reference",
                "project__id", "project__has_gig_roles", "project__title", "project__description", 
                "proposal_role__id", "proposal_role__description", "provider__email", "provider__first_name", 
                "provider__last_name", "provider__is_verified", "provider__profile__headline"
            )
            .prefetch_related(
                Prefetch(
                    "proposal_role__deliverables",
                    queryset=ProposalDeliverable.objects.only(
                        "id", "phase", "description", "duration_unit", "duration_value", "release_percentage"
                    ).order_by("rendering_order"),
                )
            )
        )
        
        return qs
