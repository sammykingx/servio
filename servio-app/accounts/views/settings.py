from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from template_map.accounts import Accounts
from accounts.models.address import AddressType


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's accounts page page.
    """

    template_name = Accounts.ACCOUNT_SETTINGS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        addresses = self.request.user.addresses

        context["home"] = addresses.filter(label=AddressType.HOME).first()
        context["billing"] = addresses.filter(label=AddressType.BILLING).first()
        context["work"] = addresses.filter(label=AddressType.WORK).first()

        return context


class BusinessSettingsView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's business settings page.
    """

    template_name = Accounts.BUSINESS_ACCOUNT_SETTINGS
