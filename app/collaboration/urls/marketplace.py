from django.urls import path, reverse_lazy
from core.url_names import MarketplaceURLS
from django.views.generic import RedirectView
from collaboration.views.marketplace import (
    OppurtunityListView, OppurtuniyDetailView, ProposalSubmissionView
)


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(MarketplaceURLS.ALL), permanent=True
        ),
    ),
     
    path("for-you/", OppurtunityListView.as_view(),
         name=MarketplaceURLS.ALL
    ),
    
    path("details/<slug:slug>/", OppurtuniyDetailView.as_view(),
         name=MarketplaceURLS.DETAIL
    ),
    path("engagement/<slug:slug>/", ProposalSubmissionView.as_view(),
         name=MarketplaceURLS.SUBMIT_PROJECT_PROPOSAL
    ),
]