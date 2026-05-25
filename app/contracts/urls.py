from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from template_map.contracts import Contract
from core.url_names import ContractURLS


urlpatterns = [
    path("preview/<uuid:proposal_id>/<uuid:role_id>",
        login_required(TemplateView.as_view(template_name=Contract.VIEW_CONTRACT)),
        name=ContractURLS.PREVIEW_CONTRACT
    ),
]