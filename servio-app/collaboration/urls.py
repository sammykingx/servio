from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from core.url_names import CollaborationURLS
from .views.list import CollaborationListView
from .views.create import CreateCollaborationView, EditGigView
from .views.detail import GigDetailView
from .views.delete import DeleteGigView
from template_map.collaboration import Collabs


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS), permanent=True
        ),
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
    path("new-collaborations", CreateCollaborationView.as_view(),
         name=CollaborationURLS.CREATE_COLLABORATION,
    ),
    path("delete/<slug:slug>", DeleteGigView.as_view(),
         name=CollaborationURLS.DELETE_COLLABORATION,
    ),
]
