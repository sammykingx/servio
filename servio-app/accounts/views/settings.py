from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from template_map.accounts import Accounts
from accounts.models.profile import UserRole
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


@login_required
def business_settings_toggle(request) -> HttpResponse:
    if request.htmx:
        state = request.GET.get("state")

        if state not in ("on", "off"):
            return HttpResponseBadRequest("Invalid state")

        new_value = (state == "on")

        profile = request.user.profile
        profile.is_business_owner = new_value
        profile.role = UserRole.PROVIDERS if new_value else UserRole.MEMBERS
        profile.save(update_fields=["is_business_owner", "role"])

    return HttpResponse(status=200)