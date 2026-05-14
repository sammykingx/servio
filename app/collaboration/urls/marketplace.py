from django.urls import path, reverse_lazy
from core.url_names import OppurtunitiesURLS
from django.views.generic import RedirectView
from collaboration.views.marketplace import (
    OppurtunityListView, OppurtuniyDetailView, AcceptOppurtuniyDetailView
)


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(OppurtunitiesURLS.ALL), permanent=True
        ),
    ),
     
    path("all/", OppurtunityListView.as_view(),
         name=OppurtunitiesURLS.ALL
    ),
    
    path("details/<slug:slug>/", OppurtuniyDetailView.as_view(),
         name=OppurtunitiesURLS.DETAIL
    ),
    path("accept-offer/<slug:slug>/", AcceptOppurtuniyDetailView.as_view(),
         name=OppurtunitiesURLS.ACCEPT_OFFER
    ),
]