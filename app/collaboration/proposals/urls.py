from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from core.url_names import ProposalURLS
from collaboration.proposals.views import ProposalListView
from template_map.collaboration import Collabs


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(ProposalURLS.LIST), permanent=True
        ),
    ),
    path("all/", ProposalListView.as_view(), name=ProposalURLS.LIST),
    path("details/<slug:slug>", TemplateView.as_view(
        template_name=Collabs.Proposals.DETAILS),
         name=ProposalURLS.DETAILS
    ),
]