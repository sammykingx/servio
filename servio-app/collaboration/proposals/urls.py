from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView
from core.url_names import ProposalURLS
from template_map.collaboration import Collabs


urlpatterns = [
    path("", TemplateView.as_view(
        template_name=Collabs.Proposals.LIST),
         name=ProposalURLS.LIST
    ),
    path("details/<slug:slug", TemplateView.as_view(
        template_name=Collabs.Proposals.DETAILS),
         name=ProposalURLS.DETAILS
    ),
]