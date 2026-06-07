from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from core.url_names import WorkroomURLS
from collaboration.views.workroom import ActivatedProjectContractView
from template_map.collaboration import Collabs


urlpatterns = [
    path("overview/",
         ActivatedProjectContractView.as_view(),
         name=WorkroomURLS.OVERVIEW
    ),
    # path("project/<slug:proj_slug>/")
]