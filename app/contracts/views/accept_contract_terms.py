from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, JsonResponse
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from contracts.application.dto import SignContractDTO
from contracts.application.services import ContractLifecycleService
from contracts.domains.errors import ContractPolicyFailure
from contracts.domains.exceptions import ContractException
from core.model_registry import registry
from core.url_names import AuthURLNames, ContractURLS
from template_map.contracts import Contract as ContractTemplates
from pydantic import ValidationError


class RoleContractTermsAcceptanceView(LoginRequiredMixin, DetailView):
    model = registry.Contract
    template_name = ContractTemplates.ACCEPT_CONTRACT_TERMS
    context_object_name = "contract"
    
    
    def dispatch(Self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))
        
    def get_object(self):
        role_id = self.kwargs.get("role_id")
        ProposalDeliverable = registry.ProposalDeliverable
        try:
            qs = (
                self.model.objects
                .select_related(
                    "proposal_role", "project", "client",
                    "provider", "provider__profile"
                )
                .only(
                    "agreed_amount", "currency", "payment_plan", "status", "client_accepted_terms_at", "reference",
                    "provider_accepted_terms_at", "client_paid_at", "completed_at", "project__id", "project__has_gig_roles", 
                    "project__title", "project__description", "proposal_role__id", "proposal_role__description", 
                    "proposal_role__role_name", "provider__email", "provider__first_name", "provider__last_name", 
                    "client__email", "client__first_name", "client__last_name", "provider__is_verified", 
                    "provider__profile__headline", "provider__profile__avatar_url"
                )
                .prefetch_related(
                    Prefetch(
                        "proposal_role__deliverables",
                        queryset=ProposalDeliverable.objects.only(
                            "id", "phase", "description", "duration_unit", "duration_value", "release_percentage"
                        ).order_by("rendering_order"),
                    )
                )
                .get(proposal_role_id=role_id)
            )
            
            return qs
        except self.model.DoesNotExist:
            raise Http404("Contract not found for this role.")

    def get_context_data(self, **kwargs):
        """Injects dynamic calculation states into template context with zero db-cost."""
        context = super().get_context_data(**kwargs)
        contract, user = self.object, self.request.user

        is_client = (user == contract.client)
        
        context["has_accepted_terms"], context["counter_party_accepted"] = (
            (contract.has_client_accepted_terms, contract.has_provider_accepted_terms) if is_client 
            else (contract.has_provider_accepted_terms, contract.has_client_accepted_terms)
        )
        
        return context
        
    def post(self, request: HttpRequest, *args, **kwargs):
        try:
            contract = self.get_object()
            SignContractDTO.model_validate_json(request.body, strict=True)
            service = ContractLifecycleService(request.user)
            contract_entity = service.to_entity(contract)
            service.accept_contract_terms(contract_entity)
            
            url = (
                reverse_lazy(ContractURLS.LIST_CONTRACTS)
                if contract.provider == request.user 
                else reverse_lazy(ContractURLS.INITIATE_CONTRACT_ACTIVATION, kwargs={"contract_slug": contract.slug})
            )
            
            return JsonResponse({
                "status": "success",
                "redirect_url": url,
            }, status=200)
            
        except Http404:
            return JsonResponse({
                "error": "Hmm, we can't seem to find that agreement.",
                "title": ContractPolicyFailure.INVALID_CONTRACT.title,
                "code": ContractPolicyFailure.INVALID_CONTRACT.code
            }, status=404)
        
        except ValidationError:
            return JsonResponse({
                "error": "Invalid data provided.",
                "title": "Validation Error",
                "code": "validation_error".upper()
            }, status=400)
            
        except ContractException as err:
            return JsonResponse({
                "error": err.message,
                "code": err.code,
                "title": err.title,
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                "error": "An unexpected error occurred. Please try again later."
            }, status=500)