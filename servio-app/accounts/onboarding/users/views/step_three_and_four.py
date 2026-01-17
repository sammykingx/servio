from django.apps import apps
from django.db.models import Prefetch
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.onboarding.users.mixins import OnboardingStepMixin
from template_map.accounts import Accounts



GigCategory = apps.get_model("collaboration", "GigCategory")


class ObjectivesView(LoginRequiredMixin, OnboardingStepMixin, TemplateView):
    template_name = Accounts.Onboarding.OBJECTIVES
    view_step = 3
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     industries = (
    #         GigCategory.objects.filter(parent__isnull=True, is_active=True)
    #         .prefetch_related(
    #             Prefetch(
    #                 "subcategories",
    #                 queryset=GigCategory.objects.filter(is_active=True).order_by("name"),
    #             )
    #         )
    #         .order_by("name")
    #     )

    #     context["taxonomy"] = [
    #         {
    #             "id": industry.id,
    #             "name": industry.name,
    #             "subcategories": [
    #                 {
    #                     "id": niche.id,
    #                     "name": niche.name,
    #                 }
    #                 for niche in industry.subcategories.all()
    #             ],
    #         }
    #         for industry in industries
    #     ]
        
    #     return context
    

class CompleteOnboardingView(LoginRequiredMixin, OnboardingStepMixin, TemplateView):
    template_name = Accounts.Onboarding.COMPLETE
    view_step = 4