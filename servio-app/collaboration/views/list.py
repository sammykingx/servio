from django.shortcuts import render
from django.db.models import Count, Sum, F, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from template_map.collaboration import Collabs


class CollaborationListView(LoginRequiredMixin, ListView):
    template_name = Collabs.LIST_COLLABORATIONS
    context_object_name = "gigs"
    paginate_by = 8

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
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        gig_status_counts = (
            self.request.user.gigs
            .aggregate(
                total=Count("id"),
                pending=Count("id", filter=Q(status="pending")),
                in_progress=Count("id", filter=Q(status="in_progress")),
                completed=Count("id", filter=Q(status="completed")),
            )
        )

        context["gig_status_counts"] = gig_status_counts
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request"):
            return render(
                self.request,
                "collaborations/partials/_gig-cards.html",
                context,
            )
        return super().render_to_response(context, **response_kwargs)


