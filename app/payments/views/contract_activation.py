from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse_lazy
from core.url_names import AuthURLNames, CollaborationURLS, ContractURLS
from core.model_registry import registry
from payments.domain.enums import PaymentType, PaymentPurpose, PaymentPhase
from payments.domain.exceptions import DomainException
from payments.services.payment_service import PaymentService
from payments.schemas.contract_activation import ContractActivationPayload
from template_map.payments import Payments
from pydantic import ValidationError
from typing import Tuple, Union
import json, logging


logger = logging.getLogger(__name__)

class ActivateContractRoleEnagementView(LoginRequiredMixin, View):
    template_name = Payments.ServicePayments.FUND_CONTRACT
    
    def get(self, request: HttpRequest, *args, **kwargs):
        contract_slug = self.kwargs.get("contract_slug")
        contract = (
            registry.Contract.objects
            .filter(slug=contract_slug)
            .first()
        )
        
        should_redirect, response = self._should_redirect(contract)
        if should_redirect:
            return response
        
        self._save_contract_to_session(contract)
        context = {
            "contract": contract
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        try:
            payload = ContractActivationPayload.model_validate_json(request.body)
            contract = self._get_contract_from_session()
            if contract is None:
                return JsonResponse({"message": "Contract information is missing from payment flow"}, status=400)
            
            payment = PaymentService(
                request=request, user=self.request.user, gateway_name="paystack", phase=PaymentPhase.INITIALIZATION
            ).initiate_payment(
                amount=contract.agreed_amount,
                payment_type=PaymentType.SERVICE,
                payment_purpose=PaymentPurpose.CONTRACT_ACTIVATION
            )
            return JsonResponse({"message": "Payment initiation endpoint. Implement payment processing logic here."}, status=200)
        
        except ValidationError:
            return JsonResponse({"message": "Invalid data provided"}, status=400)
        
        except DomainException as de:
            return JsonResponse({
                "message": de.message,
                "status": de.err_type,
                "title": de.title,
                }, status=400)
            
        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "message": "An unexpected error occurred while activating the contract. Please try again later.",
                    "status": "error",
                    "title": "Contract Activation Error"
                },
                status=500
            )

    
    def _get_contract_from_session(self):
        return self.request.session.get("contract")
    
    def _save_contract_to_session(self, contract):
        self.request.session["contract"] = contract
        self.request.session.save()
        
    def _clear_contract_from_session(self):
        self.request.session.pop("contract", None)
        self.request.session.save()
        
    def _should_redirect(self, contract) -> Tuple[bool, Union[HttpResponse, None]]:
        if contract is None:
            return True, redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))
        
        if contract.client != self.request.user:
            return True, redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS)) 

        if not contract.client_accepted_terms_at:
            return True, redirect(reverse_lazy(ContractURLS.ACCEPT_CONTRACT_TERMS), role_id=contract.proposal_role_id)
        
        return False, None
    