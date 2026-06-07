from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from core.url_names import WorkroomURLS
from collaboration.views.workroom import ContractedProjectListView
from template_map.collaboration import Collabs


urlpatterns = [
    path("overview/",
         ContractedProjectListView.as_view(),
         name=WorkroomURLS.OVERVIEW
    ),
    path("project/<slug:slug>/",
        TemplateView.as_view(template_name=Collabs.Workforce.PROJECT_WORKROOM),
        name=WorkroomURLS.PROJECT_WORKROOM
    ),
]