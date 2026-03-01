
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, Max, OuterRef
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from collaboration.models.choices import GigStatus, GigVisibility
from core.url_names import CollaborationURLS
from template_map.collaboration import Collabs
from registry_utils import get_registered_model


class ProposalRoleListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Proposals.PROPOSAL_LIST
    context_object_name = "applications"
    paginate_by = 18
    model = get_registered_model("collaboration", "ProposalRole")
    
    
    def dispatch(self, request, *args, **kwargs):
        """
        Handles invalid or unauthorized access gracefully.

        If the requested project does not exist or does not belong to the user,
        the request is redirected to the collaboration list view instead of
        raising a 404 error.
        """
        gig_slug = kwargs.get("gig_slug")
        Proposal = get_registered_model("collaboration", "Proposal")

        proposal_exists = Proposal.objects.filter(
            gig__slug=gig_slug,
            gig__creator=request.user
        ).exists()

        if not proposal_exists:
            return redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS))
    
        return super().dispatch(request, *args, **kwargs)
        
    def get_queryset(self):
        gig_slug = self.kwargs.get("gig_slug")
        proposal_status = self.request.GET.get("proposal_status")
        
        qs = (
            super().get_queryset()
            .filter(proposal__gig__slug=gig_slug)
            .order_by("-proposal__sent_At")
        )

        # if proposal_status:
        #     qs = qs.filter(proposal__status=proposal_status).distinct()
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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