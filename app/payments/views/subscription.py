from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import redirect
from core.url_names import AuthURLNames
from template_map.payments import Payments


class UserSubsriptionView(LoginRequiredMixin, TemplateView):
    pass
    # for custom routing and customizations of the user payments
    # template_name = Payments.SUBSCRIPTION
    
    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect(reverse_lazy(AuthURLNames.LOGIN))
    #     return super().dispatch(self, request,)