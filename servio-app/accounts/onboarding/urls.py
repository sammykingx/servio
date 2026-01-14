from django.urls import path
from django.views.generic import TemplateView
from .views.users import step_one
from template_map.accounts import Accounts
from core.url_names import OnboardingURLS



urlpatterns = [
    path(
        "welcome/", TemplateView.as_view(template_name=Accounts.Onboarding.START_FLOW),
        name = OnboardingURLS.Users.WELCOME   
    ),
    path(
        "users/profile-setup/", step_one.PersonalInfoView.as_view(),
        name = OnboardingURLS.Users.PROFILE_SETUP   
    ),
]