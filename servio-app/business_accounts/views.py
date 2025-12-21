from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from template_map.accounts import Accounts


class BusinessInfoView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's business settings page.
    """

    template_name = Accounts.Business.BUSINESS_INFO