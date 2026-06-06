from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from core.url_names import WorkroomURLS
from template_map.collaboration import Collabs


urlpatterns = [
    path("overview/",
         TemplateView.as_view(template_name=Collabs.Workforce.OVERVIEW),
         name=WorkroomURLS.OVERVIEW
    ),
]