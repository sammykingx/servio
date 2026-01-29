from django.urls import path
from django.views.generic import TemplateView
from core.url_names import EscrowURLS
from template_map.payments import Payments


urlpatterns = [
    path("", TemplateView.as_view(
        template_name=Payments.Escrow.OVERVIEW),
         name=EscrowURLS.OVERVIEW
    ),
    path("details/", TemplateView.as_view(
        template_name=Payments.Escrow.DETAILS),
         name=EscrowURLS.DETAILS
    ),
]