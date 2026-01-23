from django.shortcuts import render
from django.db.models import Count, Sum, F, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from template_map.collaboration import Collabs


class CollaborationListView(LoginRequiredMixin, ListView):
    template_name = Collabs.LIST_COLLABORATIONS
    context_object_name = "gigs"
    paginate_by = 4

    def get_queryset(self):
        queryset =  (
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
        
        project_status = self.request.GET.get("project_status")
        if project_status:
            print("Project status received")
            queryset = queryset.filter(status=project_status)
            
        return queryset
        
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
            status = self.request.GET.get("project_status")
            print(status)
            htmx_response = (
                "collaborations/partials/_project-list-wrapper.html"
                if status else
                "collaborations/partials/_gig-cards.html"
            )
            print(htmx_response)
            # print(context.get("page_obj").next_page_number)
            # htmx_response = "collaborations/partials/_project-list-wrapper.html"
            
            return render(self.request, htmx_response, context)
        
        return super().render_to_response(context, **response_kwargs)


