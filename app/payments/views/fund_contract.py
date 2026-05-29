from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse_lazy
from core.url_names import PaymentURLS
from core.model_registry import registry
from template_map.payments import Payments
from ..mixins import GigPaymentMixin


class FundContractRRoleView(LoginRequiredMixin, View):
    template_name = Payments.ServicePayments.FUND_CONTRACT
    
    def get(self, request: HttpRequest, *args, **kwargs):
        contract_slug = self.kwargs.get("contract_slug")
        contract = registry.Contract.objects.get(slug=contract_slug)
        context = {
            "contract_slug": contract_slug,
            "contract": contract
        }
        return render(request, self.template_name, context)