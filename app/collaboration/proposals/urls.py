from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from core.url_names import ProposalURLS
from collaboration.proposals.views import (
    RecievedProposalListView,
    ProposalRoleListView,
    SentProposalListView,
    UpdateProposalStateView,
    RenderProposalDeliverablesView
)
from template_map.collaboration import Collabs


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(ProposalURLS.RECEIVED_PROPOSALS), permanent=True
        ),
    ),
    path(
        "recieved/",
        RecievedProposalListView.as_view(),
        name=ProposalURLS.RECEIVED_PROPOSALS,
    ),
    path("update-proposals/",
         UpdateProposalStateView.as_view(),
         name=ProposalURLS.UPDATE_PROPOSAL_STATUS,
    ),
    path("sent/", SentProposalListView.as_view(), name=ProposalURLS.SENT_PROPOSALS),
    path(
        "all/<slug:gig_slug>/",
        ProposalRoleListView.as_view(),
        name=ProposalURLS.PROPOSAL_LISTINGS,
    ),
    path(
        "deliverables/<uuid:proposal_id>/",
        RenderProposalDeliverablesView.as_view(),
        name=ProposalURLS.VIEW_DELIEVERABLES,
    ),
    
]
