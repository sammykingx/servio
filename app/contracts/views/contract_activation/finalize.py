from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View

from core.model_registry import registry
from contracts.application.services import ContractLifecycleService
from contracts.domains.exceptions import ContractPolicyViolation, ContractPaymentVerificationFailure
from template_map.contracts import Contract as ContractTemplates

import logging

logger = logging.getLogger(__name__)

class FinalizeContractActivationView(LoginRequiredMixin, View):
    template_name = ContractTemplates.ACTIVATE_CONTRACT
    model = registry.Contract
    PaymentModel = registry.Payment
    
    def get(self, request: HttpRequest, *args, **kwargs):
        contract_ref = self.kwargs.get("contract_ref")
        contract_obj = get_object_or_404(self.model, reference=contract_ref)
        context = {}
        try:
            service = ContractLifecycleService(request.user)
            result = service.activate_contract(contract_obj)
            
            context["contract"] = result.contract
            context["payment"] = result.payment

        except ContractPolicyViolation as policy_err:
            context["error_title"] = policy_err.title
            context["error_message"] = policy_err.message
            context["contract"] = contract_obj
            
        except ContractPaymentVerificationFailure as payment_err:
            context["error_title"] = payment_err.title
            context["error_message"] = payment_err.message
            context["payment_required"] = True
            
        except Exception as err:
            logger.exception(err)
            context["error_message"] = "Contract activation unavailable at this time, check back later"
            
        return render(request, self.template_name, context=context)
