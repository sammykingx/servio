from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.db.models import Prefetch, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from core.model_registry import registry
from core.url_names import AuthURLNames
from template_map.proposals import Proposals as ProposalTemplates


class RenderProposalDetailView(LoginRequiredMixin, DetailView):
    model = registry.Proposal
    template_name = ProposalTemplates.DETAILS
    context_object_name = "proposal"
    pk_url_kwarg = "proposal_id"
    
    def dispatch(Self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))
        
    def get_queryset(self):
        ProposalRole = registry.ProposalRole
        ProposalDeliverable = registry.ProposalDeliverable
        
        deliverables_qs = (
            ProposalDeliverable.objects
            .only(
                "id",
                "phase",
                "description",
                "duration_unit",
                "duration_value",
                "rendering_order",
                "release_percentage",
                "created_at",
            )
            .order_by("rendering_order", "created_at")
        )
        
        roles_qs = (
            ProposalRole.objects
            .select_related("role", "category")
            .only(
                "id", "proposal_id", "client_budget", 
                "proposed_amount", "role", "category"
            )
            .prefetch_related(
                Prefetch(
                    "deliverables",
                    queryset=deliverables_qs,
                )
            )
        )
        
        qs = (
            super().get_queryset()
            .select_related("project", "provider", "provider__profile")
            .only(
                "project__has_gig_roles", "project__title", "project__description", "project__total_budget",
                "provider__first_name", "provider__last_name", "provider__is_verified", "provider__profile__headline"
            )
            .prefetch_related(
                Prefetch(
                    "roles",
                    queryset=roles_qs
                ),
            )
            .filter(
                Q(provider=self.request.user) | Q(project__creator=self.request.user)
            )
            
        )
        
        return qs
