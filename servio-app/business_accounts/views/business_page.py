from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from template_map.accounts import Accounts


class RenderBusinessPageView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's business settings page.
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models.address import AddressType
        context["work_address"] = self.request.user.addresses.filter(
            label=AddressType.WORK,
            is_business_address=True
        ).first()
        return context

    template_name = Accounts.Business.BUSINESS_PAGE