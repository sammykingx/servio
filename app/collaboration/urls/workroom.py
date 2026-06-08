from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from core.url_names import WorkroomURLS
from collaboration.views.workroom import ContractedProjectListView, ProjectWorkroomDetailView
from template_map.collaboration import Collabs


urlpatterns = [
    path("overview/",
         ContractedProjectListView.as_view(),
         name=WorkroomURLS.OVERVIEW
    ),
    path("project/<slug:slug>/",
        ProjectWorkroomDetailView.as_view(),
        name=WorkroomURLS.PROJECT_WORKROOM
    ),
]