from django.http import Http404, HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from collaboration.models.choices import ProjectStatus, PaymentOption
from proposals.domain.exceptions import ProposalError
from proposals.application.services import ProposalOrchestrationService
from collaboration.schemas.gig_role import PAYMENT_OPTIONS
from proposals.application.dto.send_proposal import ProposalSubmissionPayload
from core.model_registry import registry
from core.url_names import MarketplaceURLS, ProposalURLS
from template_map.collaboration import Collabs
from pydantic import ValidationError
import json

from proposals.domain.constants import MOCK_PROPOSAL_PAYLOAD, MALFORMED_PROPOSAL_PAYLOAD

GigCategoryModel = registry.GigCategory
GigModel = registry.Gig
GigRoleModel = registry.GigRole


class ProposalSubmissionView(LoginRequiredMixin, DetailView):
    model = GigModel
    template_name = Collabs.Marketplace.ENGAGEMENT_SUBMISSION
    context_object_name = "project"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('required_roles').filter(
            status=ProjectStatus.PUBLISHED
        ).exclude(creator=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(MarketplaceURLS.ALL))
        
    def user_can_apply_for_role(self, user, role) -> bool:
        if not user.is_authenticated:
            return False

        user_niches = set(user.profile.get_user_niches)
        return role.role_id in user_niches
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["payment_options"] = json.dumps(PAYMENT_OPTIONS)
        project = self.object
        roles = []
        if project.has_gig_roles:
            roles = project.required_roles.all()
            for role in roles:
                role.can_apply = self.user_can_apply_for_role(self.request.user, role)
        else:
            roles.extend(self.request.user.profile.get_niche_roles_list())
        context["roles"] = roles
        return context
    
    def post(self, request:HttpRequest, *args, **kwargs):
        try:
            data = ProposalSubmissionPayload.model_validate_json(request.body)
            import time
            time.sleep(5)
            # data = ProposalSubmissionPayload.model_validate(MOCK_PROPOSAL_PAYLOAD, strict=True)
            # ProposalOrchestrationService(request.user, request).submit_proposal(data)

        except ValidationError as err:
            from formatters.pydantic_formatter import format_pydantic_errors
            fields = format_pydantic_errors(err)
            print(fields)
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                },
                status=400,
            )
            
        except ProposalError as e:
            return JsonResponse({
                "status": "warning",
                "error": e.title,
                "message": e.message,
                "code": e.code,
                "url": e.redirect_url
                
            }, status=400)
            
        except Exception as err:
            message = (
                "We’ve encountered a brief hiccup while "
                "processing your request. Our team has been "
                "notified and is already looking into it. "
                "Please try again in a moment, or reach out "
                "if the issue persists."
            )
            return JsonResponse({
                "error": "Technical Alignment in-progress",
                "message": message,
            }, status=500)
 
        return JsonResponse({
            "title": "Proposal Sent!",
            "status": "success",
            "message": "High five! Your proposal is officially on its way to the creator for review. We'll let you know as soon as they take a look.",
            "url": reverse_lazy(ProposalURLS.SENT_PROPOSALS)
        })
    


