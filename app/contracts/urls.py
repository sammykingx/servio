from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from template_map.contracts import Contract
from core.url_names import ContractURLS
from .views import RoleContractTermsAcceptanceView, ContractListView, ContractTimelineView
from .views.contract_activation import StartContractActivationView, FinalizeContractActivationView


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
    path(
        "begin-activation/<slug:contract_slug>/",
        StartContractActivationView.as_view(),
        name=ContractURLS.INITIATE_CONTRACT_ACTIVATION
    ),
    path(
        "activate/<str:contract_ref>/",
        FinalizeContractActivationView.as_view(),
        name=ContractURLS.ACTIVATE_CONTRACT
    )
]