from django.urls import path
from django.views.generic import TemplateView
from .views.users import step_one
from template_map.accounts import Accounts
from core.url_names import OnboardingURLS



urlpatterns = [
    path(
        "welcome/", step_one.StartOnboardingView.as_view(),
        name = OnboardingURLS.Users.WELCOME   
    ),
    path(
        "users/personal-info/", step_one.PersonalInfoView.as_view(),
        name = OnboardingURLS.Users.PERSONAL_INFO   
    ),
]