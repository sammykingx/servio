from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Prefetch
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.url_names import CollaborationURLS
from collaboration.models.choices import PaymentOption
from template_map.collaboration import Collabs
from registry_utils import get_registered_model


GigModel = get_registered_model("collaboration","Gig")
GigRoleModel = get_registered_model("collaboration", "GigRole")
ProposalModel = get_registered_model("collaboration", "Proposal")
ProposalRoleModel = get_registered_model("collaboration", "ProposalRole")


class GigDetailView(LoginRequiredMixin, DetailView):
    """
    Displays detailed information for a single gig/project owned by the authenticated user.

    This view enforces ownership access, ensuring users can only view gigs
    they created. In addition to core gig data, it enriches the context with
    role-level payment metadata and prefetches related role proposals for
    efficient rendering.
    """
    model = GigModel
    template_name = Collabs.DETAILS
    context_object_name = "gig"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_context_data(self, **kwargs):
        """
        Extends the context with editable state rules and role payment metadata.

        Adds:
        - A list of gig statuses that allow editing
        - Computed payment details for each required role, including:
            - Payment type (full upfront or percentage split)
            - Number of installments
            - Split percentages per installment
            - Human-readable payment option label

        This metadata is structured for direct consumption by the UI layer.
        """
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

    def get_queryset(self):
        """
        Restricts gig access to user-owned records and optimizes related queries.

        The queryset:
        - Limits access to gigs created by the current user
        - Eager-loads the gig creator
        - Prefetches required roles, their associated niches, and role proposals
          along with applicant user data to minimize database queries

        Returns:
            QuerySet: An optimized queryset scoped to the authenticated user.
        """
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
        
    def fetch_proposal_roles(self, gig):
        """
        Retrieves proposal roles associated with the gig's required roles.

        This method gathers all proposal roles linked to the gig's required roles,
        including related proposal and applicant user data for comprehensive context.

        Args:
            gig (Gig): The gig instance for which to fetch proposal roles.

        Returns:
            QuerySet: A queryset of ProposalRole instances with related data.
        """
        preview_roles = (
            ProposalRoleModel.objects
            .filter(proposal__gig=gig)
            .select_related("proposal__sender__profile", "gig_role")
            .only(
                "role_amount",
                "proposed_amount",
                "gig_role__role_name",
                "proposal__sender__profile__avatar_url",
                "proposal__sender__profile__headline",
                "proposal__status",
                "proposal__sent_at",
            )
            .order_by("-proposal__created_at")[:4]
        )
        all_proposals = ProposalModel.objects.filter(gig=gig)
        role_count = {
            "total_proposals": all_proposals.count(),
            "accepted": all_proposals.filter(is_negotiating=False).count(),
            "countered": all_proposals.filter(is_negotiating=True).count()
        }
        return preview_roles, role_count
    
    def dispatch(self, request, *args, **kwargs):
        """
        Handles invalid or unauthorized access gracefully.

        If the requested gig/project does not exist or does not belong to the user,
        the request is redirected to the collaboration list view instead of
        raising a 404 error.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS))

