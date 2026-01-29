from django.urls import path
from django.views.generic import TemplateView
from .views import step_one, step_two, step_three_and_four
from template_map.accounts import Accounts
from core.url_names import OnboardingURLS

app_name = OnboardingURLS.Users.APP_NAME

urlpatterns = [
    path(
        "welcome/", step_one.StartOnboardingView.as_view(),
        name = OnboardingURLS.Users.WELCOME   
    ),
    path(
        "profile-setup/", step_one.PersonalInfoView.as_view(),
        name = OnboardingURLS.Users.PROFILE_SETUP   
    ),
    path(
        "expertise/", step_two.ExpertiseView.as_view(),
        name = OnboardingURLS.Users.EXPERTISE_AND_NICHE 
    ),
    path(
        "objectives/", step_three_and_four.ObjectivesView.as_view(),
        name = OnboardingURLS.Users.OBJECTIVES
    ),
     path(
        "complete/", step_three_and_four.CompleteOnboardingView.as_view(),
        name = OnboardingURLS.Users.COMPLETE
    ),
]