from django.urls import path
from django.views.generic.base import TemplateView
from .views import auth, registration
from core.url_names import AuthURLNames
from template_map.accounts import Accounts


urlpatterns =[
    # LOGIN AND LOGOUT
    path("access/", auth.CustomSignin.as_view(), name=AuthURLNames.LOGIN),
    path("access-code/", auth.GetLoginAccessCode.as_view(), name=AuthURLNames.LOGIN_ACCESS_CODE),
    path("access-code/verify", auth.VerifyLoginAccessCode.as_view(), name=AuthURLNames.VERIFY_ACCESS_CODE),
    # logout view
    
    # REGISTRATION
    path("join/", registration.CustomSignup.as_view(), name=AuthURLNames.SIGNUP),
    path("email/sent/", TemplateView.as_view(template_name=Accounts.Auth.SIGNUP_VERV_EMAIL_SENT), name=AuthURLNames.EMAIL_VERIFICATION_SENT),
    path("email/verify/<token>/", registration.EmailVerificationView.as_view(), name=AuthURLNames.EMAIL_CONFIRMATION),
    path("email/verified/", TemplateView.as_view(template_name=Accounts.Auth.SIGNUP_EMAIL_VERIFIED), name=AuthURLNames.EMAIL_VERIFIED),
    
    
    # ACCOUNT RECOVERY
    path("recovery-options/", TemplateView.as_view(template_name=Accounts.Auth.SIGNIN_OPTIONS), name=AuthURLNames.ACCOUNT_RECOVERY_OPTIONS),
    path("recover-account/", TemplateView.as_view(template_name=Accounts.Auth.PASSWORD_RESET), name=AuthURLNames.PASSWORD_RESET)
]
