from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from template_map.accounts import Accounts


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's accounts page page.
    """

    template_name = Accounts.ACCOUNT_SETTINGS

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user
    #     context['profile'] = getattr(user, 'profile', None)
    #     return context


class BusinessSettingsView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's business settings page.
    """

    template_name = Accounts.BUSINESS_ACCOUNT_SETTINGS
