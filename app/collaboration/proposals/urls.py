from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from core.url_names import ProposalURLS
from collaboration.proposals.views import (
    RecievedProposalListView, ProposalRoleListView, SentProposalListView
)
from template_map.collaboration import Collabs


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(ProposalURLS.RECEIVED_PROPOSALS), permanent=True
        ),
    ),
    path("recieved/", RecievedProposalListView.as_view(), name=ProposalURLS.RECEIVED_PROPOSALS),
    path("sent/", SentProposalListView.as_view(), name=ProposalURLS.SENT_PROPOSALS),
    path("all/<slug:gig_slug>/", ProposalRoleListView.as_view(), name=ProposalURLS.PROPOSAL_LISTINGS),
    path("details/<slug:slug>", TemplateView.as_view(
        template_name=Collabs.Proposals.DETAILS),
         name=ProposalURLS.DETAILS
    ),
]