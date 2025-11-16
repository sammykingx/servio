from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.profile import UserRole
from template_map.accounts import Accounts


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = Accounts.Dashboards.MEMBERS  # fallback (optional)

    def get_template_names(self):
        user = self.request.user
        role = UserRole.PROVIDERS if user.profile.is_business_owner else UserRole.MEMBERS
        # role = getattr(user.profile, "role", None)

        template_map = {
            "admin": Accounts.Dashboards.ADMIN,
            UserRole.MEMBERS: Accounts.Dashboards.MEMBERS,
            UserRole.PROVIDERS: Accounts.Dashboards.PROVIDERS,
        }

        # Return template based on role, fallback to default
        return [template_map.get(role, self.template_name)]

