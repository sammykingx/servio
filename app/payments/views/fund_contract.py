from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse_lazy
from core.url_names import AuthURLNames, CollaborationURLS, ContractURLS
from core.model_registry import registry
from template_map.payments import Payments
import json


class FundContractRRoleView(LoginRequiredMixin, View):
    template_name = Payments.ServicePayments.FUND_CONTRACT
    
    def get(self, request: HttpRequest, *args, **kwargs):
        contract_slug = self.kwargs.get("contract_slug")
        contract = (
            registry.Contract.objects
            .filter(slug=contract_slug)
            .first()
        )
        
        if contract is None:
            return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))
        
        if contract.client != request.user:
            return redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS)) 

        if not contract.client_accepted_terms_at:
            return redirect(reverse_lazy(ContractURLS.ACCEPT_CONTRACT_TERMS), role_id=contract.proposal_role_id)
        
        context = {
            "contract_slug": contract_slug,
            "contract": contract
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        # This endpoint is intended to be used as a form action for initiating the payment process.
        # The actual payment processing and verification will be handled by separate endpoints and services.
        print(json.loads(request.body))
        import time
        time.sleep(10)
        return JsonResponse({"message": "Payment initiation endpoint. Implement payment processing logic here."}, status=200)
    