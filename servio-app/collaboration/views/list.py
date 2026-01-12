from django.db.models import Count, Sum, F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from template_map.collaboration import Collabs


class CollaborationListView(LoginRequiredMixin, ListView):
    template_name = Collabs.LIST_COLLABORATIONS
    context_object_name = "gigs"
    paginate_by = 12

    def get_queryset(self):
        return (
            self.request.user.gigs
            .prefetch_related("required_roles")
            .annotate(
                role_count_db=Count("required_roles"),
                total_role_budget_db=Sum(
                    F("required_roles__budget") * F("required_roles__slots")
                ),
            )
            .order_by("-created_at")
        )

