from django.urls import path, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, TemplateView
from core.url_names import CollaborationURLS, ContractURLS
from collaboration.views.workspace import (
     CollaborationListView, CreateCollaborationView, GigDetailView,
     EditGigView, LiveEditCollaborationView, DeleteGigView
)

from collaboration.views.start_collaboration import StartCollaborationView
from template_map.collaboration import Collabs
from template_map.contracts import Contract


urlpatterns = [
     path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS), permanent=True
        ),
    ),
    path(
        "project-type/", 
        login_required(TemplateView.as_view(template_name=Collabs.Workspace.PROJECT_TYPE)), 
        name=CollaborationURLS.SELECT_COLLABORATION_TYPE
    ),
    path(
        "projects/", 
         CollaborationListView.as_view(), 
         name=CollaborationURLS.LIST_COLLABORATIONS
    ),
    path("details/<slug:slug>/", GigDetailView.as_view(),
         name=CollaborationURLS.DETAIL_COLLABORATION,
    ),
    path("modify/<slug:slug>/", EditGigView.as_view(),
         name=CollaborationURLS.EDIT_COLLABORATION,
    ),
    path("live/modify/<slug:slug>/",
         LiveEditCollaborationView.as_view(),
         name=CollaborationURLS.LIVE_COLLABORATION_EDIT,
    ),
    path("new-project", CreateCollaborationView.as_view(),
         name=CollaborationURLS.CREATE_COLLABORATION,
    ),
    path("delete/<slug:slug>", DeleteGigView.as_view(),
         name=CollaborationURLS.DELETE_COLLABORATION,
    ),
    path("view-agreement/",
         login_required(TemplateView.as_view(template_name=Contract.VIEW_CONTRACT)),
         name=ContractURLS.PREVIEW_CONTRACT,
     ),
    path("contract/<uuid:proposal_id>/<uuid:role_id>/",
         StartCollaborationView.as_view(),
         name=CollaborationURLS.START_COLLABORATION,
     ),
]
