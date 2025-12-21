from django.urls import path, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from core.url_names import BusinessURLS
from template_map.accounts import Accounts
from . import views


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(BusinessURLS.BUSINESS_INFO),
            permanent=True,
        )
    ),
    path(
        "info",
        views.BusinessInfoView.as_view(),
        name=BusinessURLS.BUSINESS_INFO,
    ),
     path(
        "profile/",
        TemplateView.as_view(template_name=Accounts.Business.BUSINESS_PROFILE),
        name="biz-temp",
        
    ),
    path(
        "services/",
        TemplateView.as_view(template_name=Accounts.Business.BUSINESS_SERVICES),
        name=BusinessURLS.SERVICES,
        
    ),
]