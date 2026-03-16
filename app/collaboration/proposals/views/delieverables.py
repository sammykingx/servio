from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.db.models import Q
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
        return (
            super().get_queryset()
            .select_related("gig")
            .filter(
                Q(sender=self.request.user) | Q(gig__creator=self.request.user)
            )
        )