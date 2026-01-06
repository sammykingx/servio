from django.db.models import Count, Sum, F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from template_map.collaboration import Collabs

# Create your views here.
class CollaborationListView(LoginRequiredMixin, TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gigs= (
            self.request.user.gigs
            .prefetch_related("required_roles")
            .annotate(
                role_count_db=Count("required_roles"),
                total_role_budget_db=Sum(
                    F("required_roles__budget") * F("required_roles__slots")
                ),
            )
        )
        context["gigs"] = gigs
        return context

    template_name = Collabs.LIST_COLLABORATIONS
    
