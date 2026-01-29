"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from template_map.accounts import Accounts
from template_map.reviews import Reviews
from core.url_names import AuthURLNames, ReviewURLS
import accounts.urls
import business_accounts.urls
import collaboration.urls
import notifications.urls
import payments.urls


handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="landing-page"),
    # path(
    #     "",
    #     RedirectView.as_view(
    #         url=reverse_lazy(AuthURLNames.LOGIN), permanent=True
    #     ),
    # ),
    # path("admin/", admin.site.urls),
    # path("allauth/", include("allauth.urls")),
    path("accounts/", include(accounts.urls)),
    path("business/", include(business_accounts.urls)),
    path("collaboration/", include(collaboration.urls)),
    path("notifications/", include(notifications.urls)),
    path("payments/", include(payments.urls)),
    # path(
    #     "client/",
    #     TemplateView.as_view(template_name=Accounts.Dashboards.MEMBERS),
    #     name="user-dashboard",
    # ),
    # path(
    #     "reviews/",
    #     TemplateView.as_view(template_name=Reviews.BUSINESS_REVIEWS),
    #     name=ReviewURLS.OVERVIEW
    # ),
    # path("kyc", TemplateView.as_view(template_name="account/kyc.html"), name="kyc-view"),
    # path("kyc-1", TemplateView.as_view(template_name="account/biz-kyc.html"), name="biz-director-view"),
    # path("kyc-2", TemplateView.as_view(template_name="account/kyc-2.html"), name="biz-doc-view"),
    # path("kyc-3", TemplateView.as_view(template_name="account/kyc-3.html"), name="kyc-3-view"),
    # path("kyc-4", TemplateView.as_view(template_name="account/kyc-4.html"), name="kyc-4-view"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    