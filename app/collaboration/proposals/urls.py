from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from core.url_names import ProposalURLS
from collaboration.proposals.views import GigProposalListView, ProposalRoleListView
from template_map.collaboration import Collabs


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(ProposalURLS.GIG_WITH_PROPOSALS_LIST), permanent=True
        ),
    ),
    path("all/", GigProposalListView.as_view(), name=ProposalURLS.GIG_WITH_PROPOSALS_LIST),
    path("all/<slug:gig_slug>/", ProposalRoleListView.as_view(), name=ProposalURLS.PROPOSAL_LISTINGS),
    path("details/<slug:slug>", TemplateView.as_view(
        template_name=Collabs.Proposals.DETAILS),
         name=ProposalURLS.DETAILS
    ),
]