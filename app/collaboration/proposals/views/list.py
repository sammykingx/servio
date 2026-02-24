
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef
from django.views.generic import ListView
from collaboration.models.choices import GigStatus, GigVisibility
from template_map.collaboration import Collabs
from registry_utils import get_registered_model


class ProposalListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Proposals.LIST
    context_object_name = "proposals"
    paginate_by = 8
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
            .annotate(has_proposals=Exists(proposals))
            .filter(has_proposals=True)
            .order_by("-created_at")
        )
        
        proposal_status = self.request.GET.get("proposal_status")

        if proposal_status:
            base_qs = base_qs.filter(proposals__status=proposal_status).distinct()
        
        return base_qs