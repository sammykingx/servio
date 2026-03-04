
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, F, OuterRef, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views.generic import ListView
from collaboration.models.choices import GigStatus, GigVisibility, ProposalStatus
from template_map.collaboration import Collabs
from registry_utils import get_registered_model
from decimal import Decimal


class GigProposalListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Proposals.RECEIVED_PROPOSALS
    context_object_name = "gigs"
    paginate_by = 7
    model = get_registered_model("collaboration", "Gig")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get_queryset(self):
        Proposal = get_registered_model("collaboration", "Proposal")
        proposals = Proposal.objects.filter(gig=OuterRef("pk"))
        base_qs = (
            super().get_queryset()
            .filter(
                creator=self.request.user,
                status=GigStatus.PUBLISHED,
                visibility=GigVisibility.PUBLIC,
                is_gig_active=True
            )
        )
        
        gigs = (
            base_qs
            .annotate(total_proposals=Count("proposals"))
            .annotate(has_proposals=Exists(proposals))
            # .annotate(latest_proposal_date=Max("proposals__created_at"))
            .filter(has_proposals=True)
            .order_by("created_at")
            # .order_by("-latest_proposal_date")
        )
        
        proposal_status = self.request.GET.get("proposal_status")

        if proposal_status:
            base_qs = base_qs.filter(proposals__status=proposal_status).distinct()
        
        return gigs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        Proposal = get_registered_model("collaboration", "Proposal")
        ProposalRole = get_registered_model("collaboration", "ProposalRole")

        proposal_filter = Q(
            proposal__gig__creator=self.request.user,
            proposal__gig__status=GigStatus.PUBLISHED,
            proposal__gig__visibility=GigVisibility.PUBLIC,
            proposal__gig__is_gig_active=True,
        )

        metrics = ProposalRole.objects.filter(
            proposal_filter
        ).aggregate(
            total_proposals=Count(
                "proposal",
                distinct=True
            ),
            negotiating_worth=Coalesce(
                Sum(
                    "proposed_amount",
                    filter=Q(proposal__is_negotiating=True)
                ),
                Decimal("0.00")
            ),
            accepted_worth=Coalesce(
                Sum(
                    "role_amount",
                    filter=Q(proposal__is_negotiating=False)
                ),
                Decimal("0.00")
            )
        )

        context.update(metrics)
        return context
    
    def render_to_response(self, context, **response_kwargs):
        """
        Renders the response differently for HTMX requests.

        - HTMX requests return a partial template for dynamic page updates
        - Standard requests fall back to the default ListView rendering
        """
        if self.request.headers.get("HX-Request"):
            htmx_response = None
            return render(self.request, htmx_response, context)
        
        return super().render_to_response(context, **response_kwargs)