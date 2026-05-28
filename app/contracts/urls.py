from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from template_map.contracts import Contract
from core.url_names import ContractURLS
from .views import RoleContractTermsAcceptanceView, ContractListView, ContractTimelineView

urlpatterns = [
    path("accept-terms/<uuid:role_id>",
        RoleContractTermsAcceptanceView.as_view(),
        name=ContractURLS.ACCEPT_CONTRACT_TERMS
    ),
    path(
        "my-contracts/",
        ContractListView.as_view(),
        name=ContractURLS.LIST_CONTRACTS
    ),
    path(
        "timeline/<slug:contract_slug>/",
        ContractTimelineView.as_view(),
        name=ContractURLS.CONTRACT_TIMELINE
    ),
]