from django.apps import apps
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.onboarding.users.mixins import OnboardingStepMixin
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
        try:
            payload = json.loads(request.body)

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400,
            )
            
        import time
        time.sleep(5)
        
        return JsonResponse(
            {"status": "success", "url": ""},
            status=200
        )