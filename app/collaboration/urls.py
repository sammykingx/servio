from django.urls import path, include, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, TemplateView
from core.url_names import CollaborationURLS, ContractURLS
from .views.list import CollaborationListView
from .views.create import CreateCollaborationView
from .views.modify import EditGigView, LiveEditCollaborationView
from .views.detail import GigDetailView
from .views.delete import DeleteGigView
from .views.start_collaboration import StartCollaborationView
from .proposals import urls as proposal_urls
from .oppurtunities import urls as oppurtunity_urls
from template_map.collaboration import Collabs

urlpatterns = [
     path("proposals/", include(proposal_urls)),
     path("oppurtunities/", include(oppurtunity_urls)),
     path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS), permanent=True
        ),
    ),
    path(
        "select-type/", 
        login_required(TemplateView.as_view(template_name=Collabs.SELECT_TYPE)), 
        name=CollaborationURLS.SELECT_COLLABORATION_TYPE
    ),
    path(
        "all-collaborations/", 
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
    path("new-collaborations", CreateCollaborationView.as_view(),
         name=CollaborationURLS.CREATE_COLLABORATION,
    ),
    path("delete/<slug:slug>", DeleteGigView.as_view(),
         name=CollaborationURLS.DELETE_COLLABORATION,
    ),
    path("view-agreement/",
         login_required(TemplateView.as_view(template_name=Collabs.Contracts.VIEW_CONTRACT)),
         name=ContractURLS.PREVIEW_CONTRACT,
     ),
    path("contact/<uuid:proposal_id>/<uuid:role_id>/",
         StartCollaborationView.as_view(),
         name=CollaborationURLS.START_COLLABORATION,
     ),
]
