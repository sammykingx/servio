from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView
from core.url_names import ProposalURLS
from .views import (
    RecievedProposalListView,
    ProposalRoleListView,
    SentProposalListView,
    UpdateProposalStateView,
    RenderProposalDetailView
)


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
    path("sent/", SentProposalListView.as_view(), name=ProposalURLS.SENT_PROPOSALS),
    path("update-proposals/",
         UpdateProposalStateView.as_view(),
         name=ProposalURLS.UPDATE_PROPOSAL_STATUS,
    ),
    path(
        "project/<slug:project_slug>/",
        ProposalRoleListView.as_view(),
        name=ProposalURLS.PROPOSAL_LISTINGS,
    ),
    path(
        "details/<uuid:proposal_id>/",
        RenderProposalDetailView.as_view(),
        name=ProposalURLS.VIEW_DETAILS,
    ),
    
]
