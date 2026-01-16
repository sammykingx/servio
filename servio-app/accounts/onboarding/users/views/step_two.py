from django.views.generic import TemplateView
from core.url_names import OnboardingURLS
from template_map.accounts import Accounts


class ExpertiseView(TemplateView):
    template_name = Accounts.Onboarding.EXPERTISE