from django.http import Http404, HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from collaboration.models.choices import ProjectStatus, PaymentOption
from proposals.domain.exceptions import ProposalError
from proposals.application.services import ProposalSubmissionService
from collaboration.schemas.gig_role import PAYMENT_OPTIONS
from proposals.application.dto.send_proposal import ProposalSubmissionPayload
from core.model_registry import registry
from core.url_names import MarketplaceURLS, ProposalURLS
from template_map.collaboration import Collabs
from pydantic import ValidationError
import json


GigCategoryModel = registry.GigCategory
GigModel = registry.Gig
GigRoleModel = registry.GigRole


class ProposalSubmissionView(LoginRequiredMixin, DetailView):
    """
    Handles both the rendering and processing of project proposal submissions.

    **Core Objectives:**
    1. Provide service providers with an interface displaying target project details, 
       available roles, matching eligibility, and standard payment options (GET).
    2. Securely ingest, validate, and orchestrate the parsing of a provider's multi-layered 
       proposal terms via a strict Pydantic JSON payload interface (POST).

    **Operational Routing & Guardrails:**
    - Requires authentication; automatically redirects unauthenticated requests.
    - Isolates projects by enforcing that only `PUBLISHED` status projects are viewable.
    - Blocks creators from bidding on their own projects via query exclusions.
    - Catches missing/hidden records (`Http404`) and gracefully reverts users back 
      to the primary marketplace index.

    Attributes:
        model (Model): Target model backing the detail lookup (`GigModel`).
        template_name (str): Path to the layout for engagement configurations.
        context_object_name (str): Variable name alias assigned within the template (`project`).
        slug_field (str): Database field name used for URL keyword resolution ('slug').
        slug_url_kwarg (str): URL pattern keyword argument capturing identifier token ('slug').
    """
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
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["payment_options"] = json.dumps(PAYMENT_OPTIONS)
        project = self.object
        user_niches = set(self.request.user.profile.get_user_niches)
        roles = []
        if project.has_gig_roles:
            roles = project.required_roles.all()
            for role in roles:
                if role.role_id in user_niches:
                    role.can_apply = True
        else:
            roles.extend(self.request.user.profile.get_niche_roles_list())
        context["roles"] = roles
        return context
    
    def post(self, request:HttpRequest, *args, **kwargs):
        try:
            data = ProposalSubmissionPayload.model_validate_json(request.body, strict=True)
            ProposalSubmissionService(self.request.user, request).submit_proposal(data)

        except ValidationError as err:
            from formatters.pydantic_formatter import format_pydantic_errors
            fields = format_pydantic_errors(err)
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                    "status": "warning",
                    "data": fields
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
            print(err)
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "status": "warning",
                "error": "Technical Alignment in-progress",
                "message": "An unexpected server error occurred. Please try again in a moment.",
            }, status=500)
 
        return JsonResponse({
            "title": "Proposal Sent!",
            "status": "success",
            "message": "High five! Your proposal is officially on its way to the creator for review. We'll let you know as soon as they take a look.",
            "url": reverse_lazy(ProposalURLS.SENT_PROPOSALS)
        })
    