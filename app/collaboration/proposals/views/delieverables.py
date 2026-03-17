from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.db.models import Prefetch, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from core.url_names import AuthURLNames
from registry_utils import get_registered_model
from template_map.collaboration import Collabs


class RenderProposalDeliverablesView(LoginRequiredMixin, DetailView):
    model = get_registered_model("collaboration", "Proposal")
    template_name = Collabs.Proposals.VIEW_DELIEVERABLES
    context_object_name = "proposal"
    pk_url_kwarg = "proposal_id"
    
    def dispatch(Self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))
        
    def get_queryset(self):
        ProposalRole = get_registered_model("collaboration", "ProposalRole")
        ProposalDeliverable = get_registered_model("collaboration", "ProposalDeliverable")
        
        qs = (
            super().get_queryset()
            .select_related("gig", "sender", "sender__profile")
            .only(
                "gig__has_gig_roles", "gig__title", "gig__description", "gig__total_budget",
                "sender__first_name", "sender__last_name", "sender__is_verified", "sender__profile__headline"
            )
            .prefetch_related(
                Prefetch(
                    "roles",
                    queryset=ProposalRole.objects.only(
                        "id", "proposal_id", "role_amount", 
                        "proposed_amount", "gig_role", "gig_category"
                    )
                ),
                Prefetch(
                    "deliverables",
                    queryset=(
                        ProposalDeliverable.objects
                        .order_by("order")
                    )
                )
            )
            .filter(
                Q(sender=self.request.user) | Q(gig__creator=self.request.user)
            )
            
        )
        
        return qs