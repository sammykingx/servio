from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from template_map.contracts import Contract
from core.url_names import ContractURLS
from .views import RenderProposalRoleContractView

urlpatterns = [
    path("preview/<uuid:role_id>",
        RenderProposalRoleContractView.as_view(),
        name=ContractURLS.PREVIEW_CONTRACT
    ),
]