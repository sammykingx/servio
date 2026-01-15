from django.views.generic import TemplateView
from core.url_names import OnboardingURLS
from template_map.accounts import Accounts
from .. import BaseOnboardingView


class ExpertiseView(BaseOnboardingView, TemplateView):
    template_name = Accounts.Onboarding.EXPERTISE