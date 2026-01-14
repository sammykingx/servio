from django.views.generic import TemplateView
from core.url_names import OnboardingURLS
from template_map.accounts import Accounts
from .. import BaseOnboardingView


class StartOnboardingView(BaseOnboardingView, TemplateView):
    template_name = Accounts.Onboarding.START_FLOW

class PersonalInfoView(BaseOnboardingView, TemplateView):
    template_name = Accounts.Onboarding.PERSONAL_INFO