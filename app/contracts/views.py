from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, JsonResponse
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from contracts.application.dto import SignContractDTO
from contracts.application.services import ContractSigningService
from contracts.domains.errors import ContractPolicyFailure
from contracts.domains.exceptions import ContractException
from core.model_registry import registry
from core.url_names import AuthURLNames
from template_map.contracts import Contract as ContractTemplates
from pydantic import ValidationError


class RenderProposalRoleContractView(LoginRequiredMixin, DetailView):
    model = registry.Contract
    template_name = ContractTemplates.VIEW_CONTRACT
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
                    "agreed_amount", "currency", "payment_plan", "status", "signed_at", "reference",
                    "project__id", "project__has_gig_roles", "project__title", "project__description", 
                    "proposal_role__id", "proposal_role__description", "proposal_role__role_name", 
                    "provider__email", "provider__first_name", "provider__last_name", "client__email", 
                    "client__first_name", "client__last_name", "provider__is_verified", 
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
        contract = self.object
        user = self.request.user

        has_signed = False
        if user == contract.client:
            has_signed = contract.has_client_signed
        elif user == contract.provider:
            has_signed = contract.has_provider_signed

        context["has_signed"] = has_signed
        return context
    
    def post(self, request: HttpRequest, *args, **kwargs):
        try:
            contract = self.get_object()
            SignContractDTO.model_validate_json(request.body, strict=True)
            service = ContractSigningService(request.user)
            contract_entity = service.to_entity(contract)
            service.sign_contract(contract_entity)

            return JsonResponse({
                "status": "success",
                "redirect_url": request.path,
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