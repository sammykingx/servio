from django.urls import path
from django.views.generic import TemplateView
from .views.users import step_one, step_two
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
    path(
        "users/expertise/", step_two.ExpertiseView.as_view(),
        name = OnboardingURLS.Users.EXPERTISE_AND_NICHE 
    ),
    path(
        "users/objectives/", TemplateView.as_view(template_name=Accounts.Onboarding.OBJECTIVES),
        name = OnboardingURLS.Users.OBJECTIVES
    ),
     path(
        "complete/", TemplateView.as_view(template_name=Accounts.Onboarding.COMPLETE),
        name = OnboardingURLS.Users.COMPLETE
    ),
]