from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from template_map.accounts import Accounts


class BusinessInfoView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's business settings page.
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from constants import biz_categories
        context["industry_obj"] = biz_categories.get_industry_obj()
        
        return context

    template_name = Accounts.Business.BUSINESS_INFO
    
    
class RegisterBusinessAccount(LoginRequiredMixin, View):
    http_method_names = ["post"]
    
    def post(self, request, *args, **kwargs):
        return HttpResponse()