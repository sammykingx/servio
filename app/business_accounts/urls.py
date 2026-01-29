from django.urls import path, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from core.url_names import BusinessURLS
from template_map.accounts import Accounts
from template_map.reviews import Reviews
from template_map.invoice import Invoices
from template_map.marketing import Marketing
from template_map.payments import Payments
from template_map.collaboration import Collabs
from .views import register, business_page


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(BusinessURLS.BUSINESS_ONBOARDING),
            permanent=True,
        )
    ),
    path(
        "business-onboarding/",
        register.RenderBusinessRegistrationView.as_view(),
        name=BusinessURLS.BUSINESS_ONBOARDING,
    ),
    path(
        "register-business/",
        register.RegisterBusinessAccount.as_view(),
        name=BusinessURLS.REGISTER_BUSINESS,
    ),
     path(
        "upload-business-logo/",
        register.UploadBusinessLogoView.as_view(),
        name=BusinessURLS.UPLOAD_BUSINESS_LOGO,
    ),
     path(
        "business-page/",
        business_page.RenderBusinessPageView.as_view(),
        name=BusinessURLS.VIEW_BUSINESS_PAGE,
        
    ),
    path(
        "services/",
        TemplateView.as_view(template_name=Accounts.Business.BUSINESS_SERVICES),
        name=BusinessURLS.SERVICES,   
    ),
    path(
        "schedule/",
        TemplateView.as_view(template_name=Accounts.Business.BUSINESS_SCHEDULE),
        name=BusinessURLS.SCHEDULE,
    ),
    path(
        "marketing/", TemplateView.as_view(template_name=Marketing.SUMMARY),
        name="biz-marketing"
    ),
    path("invoice/", TemplateView.as_view(template_name=Invoices.SUMMARY),
         name="biz-invoice",
    ),
    path("create-invoice/", TemplateView.as_view(template_name=Invoices.CREATE_INVOICE),
         name="create-invoice",
    ),
    path("booking-rules/", TemplateView.as_view(template_name=Accounts.Business.BUSINESS_BOOKING_RULE),
         name="booking-rules",
    ),
]