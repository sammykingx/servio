from django.urls import path
from django.views.generic import TemplateView
from core.url_names import SmartReleaseURLS
from template_map.smart_release import SmartReleaseTemplates


urlpatterns = [
    path("", TemplateView.as_view(
        template_name=SmartReleaseTemplates.OVERVIEW),
         name=SmartReleaseURLS.OVERVIEW
    ),
]