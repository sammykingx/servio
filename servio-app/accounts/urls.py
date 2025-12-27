from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LogoutView
from .views import (
    auth,
    registration,
    password,
    dashboard,
    settings,
    account_updates,
)
from core.url_names import AuthURLNames
from template_map.accounts import Accounts


urlpatterns = [
    # LOGIN AND LOGOUT
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(AuthURLNames.LOGIN), permanent=True
        ),
    ),
    path(
        "access/",
        auth.CustomSignin.as_view(),
        name=AuthURLNames.LOGIN,
    ),
    path(
        "access-code/",
        auth.SigninLinkView.as_view(),
        name=AuthURLNames.LOGIN_LINK,
    ),
    path(
        "access-code/verify/<token>/",
        auth.VerifySigninLinkView.as_view(),
        name=AuthURLNames.VERIFY_LOGIN_LINK,
    ),
    path("sign-out/", LogoutView.as_view(), name=AuthURLNames.LOGOUT),
    
    # REGISTRATION
    path(
        "join/",
        registration.CustomSignup.as_view(),
        name=AuthURLNames.SIGNUP,
    ),
    path(
        "email/sent/",
        TemplateView.as_view(
            template_name=Accounts.Auth.SIGNUP_VERV_EMAIL_SENT
        ),
        name=AuthURLNames.EMAIL_VERIFICATION_SENT,
    ),
    path(
        "email/verify/<token>/",
        registration.EmailVerificationView.as_view(),
        name=AuthURLNames.EMAIL_CONFIRMATION,
    ),
    
    # ACCOUNT RECOVERY
    path(
        "recovery-options/",
        TemplateView.as_view(template_name=Accounts.Auth.SIGNIN_OPTIONS),
        name=AuthURLNames.ACCOUNT_RECOVERY_OPTIONS,
    ),
    path(
        "request-password-reset/",
        password.PasswordResetEmailView.as_view(),
        name=AuthURLNames.REQUEST_PASSWORD_RESET,
    ),
    
    # PASSWORD RESET
    path(
        "password-reset/<token>/",
        password.NewPasswordView.as_view(),
        name=AuthURLNames.PASSWORD_RESET,
    ),
    path(
        "change-password/",
        password.ChangePasswordView.as_view(),
        name=AuthURLNames.PASSWORD_CHANGE,
    ),
    
    # DASHBOARD
    path(
        "dashboard/",
        dashboard.DashboardView.as_view(),
        name=AuthURLNames.ACCOUNT_DASHBOARD,
    ),
    path(
        "profile/",
        dashboard.ProfileView.as_view(),
        name=AuthURLNames.ACCOUNT_PROFILE,
    ),
    path(
        "settings/",
        settings.AccountSettingsView.as_view(),
        name=AuthURLNames.ACCOUNT_SETTINGS,
    ),
    path(
        "update/social-links/",
        account_updates.UpdateSocialLinksView.as_view(),
        name=AuthURLNames.UPDATE_SOCIAL_LINKS,
    ),
    path(
        "update/profile-info/",
        account_updates.UpdatePersonalInfoView.as_view(),
        name=AuthURLNames.UPDATE_PROFILE_INFO,
    ),
    path(
        "update/address-info/",
        account_updates.UpdateAddressView.as_view(),
        name=AuthURLNames.UPDATE_ADDRESS_INFO,
    ),
    path(
        "upload/profile-picture/",
        account_updates.UpdateProfilePictureView.as_view(),
        name=AuthURLNames.UPLOAD_PROFILE_PICTURE,
    ),
    path(
        "become-provider/",
        settings.business_settings_toggle,
        name=AuthURLNames.SWITCH_TO_BUSINESS,
    ),
    
]
