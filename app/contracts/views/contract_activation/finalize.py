from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View

from core.model_registry import registry
from contracts.application.services import ContractLifecycleService
from template_map.contracts import Contract as ContractTemplates


class FinalizeContractActivationView(LoginRequiredMixin, View):
    template_name = ContractTemplates.ACTIVATE_CONTRACT
    model = registry.Contract
    PaymentModel = registry.Payment
    
    def get(self, request: HttpRequest, *args, **kwargs):
        contract_ref = self.kwargs.get("contract_ref")
        # contract_service = ContractLifecycleService(request.user).activate_contract(contract_ref)
        contract = get_object_or_404(self.model, reference=contract_ref)
        payment = self.PaymentModel.objects.filter(
            contract_ref=contract.reference,
            user=request.user
        ).order_by('-created_at').first()
        
        context = {
            "contract": contract,
            "payment": payment,
        }
        return render(request, self.template_name, context=context)