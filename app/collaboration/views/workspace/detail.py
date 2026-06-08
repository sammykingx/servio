from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Prefetch
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from core.model_registry import registry
from core.url_names import CollaborationURLS
from collaboration.models.choices import PaymentOption
from proposals.models.choices import ProposalStatus, ProposalRoleStatus
from template_map.collaboration import Collabs


GigModel = registry.Gig
GigRoleModel = registry.GigRole
ProposalModel = registry.Proposal
ProposalRoleModel = registry.ProposalRole


class GigDetailView(LoginRequiredMixin, DetailView):
    """
    Displays detailed information for a single gig/project owned by the authenticated user.
    """
    model = GigModel
    template_name = Collabs.Workspace.DETAILS
    context_object_name = "gig"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS))

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(creator=self.request.user)
            .select_related("creator")
            .prefetch_related(
                Prefetch(
                    "required_roles",
                    queryset=GigRoleModel.objects.select_related("niche"),
                )
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal_roles, proposal_count = self.fetch_proposal_roles(self.object)
        
        context["editable_statuses"] = ["pending", "draft"]
        context["proposal_roles"] = proposal_roles
        context["proposal_count"] = proposal_count
        
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
        
    def fetch_proposal_roles(self, gig):
        """
        Retrieves proposal roles associated with the gig's required roles.
        """
        all_proposals = ProposalModel.objects.filter(project=gig)
        
        preview_roles = (
            ProposalRoleModel.objects
            .filter(proposal__project=gig, status__in=[ProposalRoleStatus.PENDING, ProposalRoleStatus.ACCEPTED, ProposalRoleStatus.REJECTED])
            .select_related("proposal__provider__profile", "role") 
            .only(
                "id",
                "proposal__id",
                "proposed_amount",
                "role__role_name",
                "role_name",
                "proposal__provider__profile__avatar_url",
                "proposal__provider__profile__headline",
                "proposal__status",
                "proposal__sent_at",
            )
            .order_by("-proposal__created_at")[:4]
        )
        
        proposal_count = {
            "total_proposals": all_proposals.count(),
            "accepted": all_proposals.filter(status=ProposalStatus.ACCEPTED).count(),
            "reviewed": all_proposals.filter(status=ProposalStatus.REVIEWED).count()
        }
        return preview_roles, proposal_count
    