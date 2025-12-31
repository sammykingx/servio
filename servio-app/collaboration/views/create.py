from django.apps import apps
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from template_map.collaboration import Collabs
import json


GigCategory = apps.get_model("collaboration", "GigCategory")

class CreateCollaborationView(LoginRequiredMixin, TemplateView):
    """
    Docstring for CreateCollaborationView
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        niches = (
            GigCategory.objects
            .filter(parent__isnull=True, is_active=True)
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=GigCategory.objects.filter(is_active=True).order_by("name")
                )
            )
            .order_by("name")
        )

        taxonomy = [
            {
                "id": niche.id,
                "name": niche.name,
                "subcategories": [
                    {
                        "id": sub.id,
                        "name": sub.name,
                    }
                    for sub in niche.subcategories.all()
                ],
            }
            for niche in niches
        ]

        context["gig_taxonomy"] = json.dumps(taxonomy)
        
        return context

    template_name = Collabs.CREATE