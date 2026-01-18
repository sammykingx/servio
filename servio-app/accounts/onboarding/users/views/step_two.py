from django.apps import apps
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from pydantic import ValidationError
from accounts.onboarding.exception import OnboardingError
from accounts.onboarding.manager import UserOnboardingManager
from accounts.onboarding.schemas import OnboardingStepTwoPayload
from accounts.onboarding.users.mixins import OnboardingStepMixin
from formatters.pydantic_formatter import format_pydantic_errors
from template_map.accounts import Accounts
import json



GigCategory = apps.get_model("collaboration", "GigCategory")


class ExpertiseView(LoginRequiredMixin, OnboardingStepMixin, TemplateView):
    template_name = Accounts.Onboarding.EXPERTISE
    view_step = 2
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        industries = (
            GigCategory.objects.filter(parent__isnull=True, is_active=True)
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=GigCategory.objects.filter(is_active=True).order_by("name"),
                )
            )
            .order_by("name")
        )

        context["taxonomy"] = [
            {
                "id": industry.id,
                "name": industry.name,
                "subcategories": [
                    {
                        "id": niche.id,
                        "name": niche.name,
                    }
                    for niche in industry.subcategories.all()
                ],
            }
            for industry in industries
        ]
        
        return context
    
    def post(self, request, *args, **kwargs):
        manager = UserOnboardingManager(self.request.user)
        try:
            payload = json.loads(request.body)
            data = OnboardingStepTwoPayload(**payload)
            industry_obj, niche_objs = self.validate_payload_data(payload)
            self.update_profile_data(data, industry_obj, niche_objs)
            
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400,
            )
        
        except ValidationError as e:
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                    "fields": format_pydantic_errors(e),
                },
                status=400,
            )
            
        except OnboardingError as err:
            return JsonResponse(
                {
                    "error": err.title,
                    "message": err.message,
                },
                status=400,
            )
            
        except Exception:
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {
                    "error": "Something went wrong",
                    "message": "We couldn’t complete your request. Please try again shortly.",
                },
                status=400,
            )
        
        return JsonResponse(
            {"status": "success", "redirect_url": manager.advance_user()},
            status=200
        )
        
    def validate_payload_data(self, payload):
        industry = payload.get("industry")
        niches = payload.get("niches", [])

        try:
            industry_obj = GigCategory.objects.get(
                id=industry["id"],
                parent__isnull=True,
                is_active=True,
            )
        except GigCategory.DoesNotExist:
            raise OnboardingError(
                title="Please choose a valid industry",
                message="The industry you selected is no longer available. Please choose another one.",
                internal_reason="invalid_or_inactive_industry",
            )
                
        # indutry name integrity check
        if industry_obj.name != industry.get("name"):
            raise OnboardingError(
                title="Industry selection needs attention",
                message="Please reselect your industry to continue.",
                internal_reason="industry_name_mismatch",
            )
            
        if len(niches) > 3:
            raise OnboardingError(
                title="Too many selections",
                message="You can choose up to three niches.",
                internal_reason="niche_limit_exceeded",
            )

        niche_ids = [niche["id"] for niche in niches]

        niche_qs = GigCategory.objects.filter(
            id__in=niche_ids,
            parent=industry_obj,
            is_active=True,
        )

        if niche_qs.count() != len(niche_ids):
            raise OnboardingError(
                title="Some selections aren’t available",
                message="One or more selected niches can’t be used. Please review your choices.",
                internal_reason="invalid_or_mismatched_niches",
            )

        # Niche Name integrity check
        niche_map = {n.id: n.name for n in niche_qs}
        for n in niches:
            if niche_map.get(n["id"]) != n.get("name"):
                raise OnboardingError(
                    title="Niche selection needs attention",
                    message="Please reselect your niches to continue.",
                    internal_reason="niche_name_mismatch",
                )

        return industry_obj, list(niche_qs)
    
    
    def update_profile_data(self, data, industry_obj, niche_objs):
        profile = self.request.user.profile

        with transaction.atomic():
            profile.industry = industry_obj
            profile.bio = data.bio.strip()
            profile.save()

            profile.niches.set(niche_objs)