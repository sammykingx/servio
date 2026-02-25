
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, Max, OuterRef
from django.shortcuts import render
from django.views.generic import ListView
from collaboration.models.choices import GigStatus, GigVisibility
from template_map.collaboration import Collabs
from registry_utils import get_registered_model


class ProposalListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Proposals.LIST
    context_object_name = "gigs"
    paginate_by = 18
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