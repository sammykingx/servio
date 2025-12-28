from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.profile import UserRole
from accounts.models.address import AddressType
from template_map.accounts import Accounts


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = Accounts.Dashboards.MEMBERS

    def get_template_names(self):
        user = self.request.user
        role = getattr(user.profile, "role", UserRole.MEMBERS)

        template_map = {
            UserRole.ADMIN: Accounts.Dashboards.ADMIN,
            UserRole.MEMBERS: Accounts.Dashboards.MEMBERS,
            UserRole.PROVIDERS: Accounts.Dashboards.PROVIDERS,
            UserRole.STAFF: Accounts.Dashboards.STAFFS,
        }

        if user.is_verified is False:
            messages.warning(
                self.request,
                "Please verify your email to access all features.",
                extra_tags="Email Not Verified",
            )
        # Return template based on role, fallback to default
        return [template_map.get(role, self.template_name)]


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's profile page.
    """

    template_name = Accounts.ACCOUNT_PROFILE

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        addresses = self.request.user.addresses
        ctx["social_links"] = {
            link.platform: link.url
            for link in self.request.user.social_links.all()
        }

        ctx["home"] = addresses.filter(label=AddressType.HOME).first()
        return ctx
