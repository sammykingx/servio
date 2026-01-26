from django.shortcuts import render
from django.db.models import Count, Sum, F, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from template_map.collaboration import Collabs


class CollaborationListView(LoginRequiredMixin, ListView):
    """
    Displays a paginated list of gigs and projects created by the authenticated user.

    The view supports:
    - Filtering projects by status via query parameters
    - Aggregating role-related metadata for each gig
    - Providing summary counts of projects grouped by status
    - Partial rendering for HTMX-based UI updates
    """
    
    template_name = Collabs.LIST_COLLABORATIONS
    context_object_name = "gigs"
    paginate_by = 12

    def get_queryset(self):
        """
        Returns the user's gigs enriched with role and budget metadata.

        The queryset:
        - Includes only gigs created by the current user
        - Prefetches related roles to minimize database queries
        - Annotates each gig with:
            - Total number of required roles
            - Aggregate budget across all roles and slots
        - Supports optional filtering by project status via query parameters
        - Orders results by most recently created gigs first

        Returns:
            QuerySet: A filtered and annotated queryset of user-owned gigs.
        """
        
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
            queryset = queryset.filter(status=project_status)
            
        return queryset
        
    def get_context_data(self, **kwargs):
        """
        Extends the template context with aggregate project status metrics.

        Adds a summary object containing:
        - Total number of user-created gigs
        - Count of gigs grouped by lifecycle status

        This data is primarily used for dashboard-style UI elements
        such as status tabs, counters, or filters.
        """
        from collaboration.models.choices import GigStatus
        context = super().get_context_data(**kwargs)

        gig_status_counts = (
            self.request.user.gigs
            .aggregate(
                total=Count("id"),
                published=Count("id", filter=Q(status=GigStatus.PUBLISHED)),
                pending=Count("id", filter=Q(status=GigStatus.PENDING)),
                in_progress=Count("id", filter=Q(status=GigStatus.IN_PROGRESS)),
                completed=Count("id", filter=Q(status=GigStatus.COMPLETED)),
            )
        )
        context["gig_status_counts"] = gig_status_counts
        return context
    
    def render_to_response(self, context, **response_kwargs):
        """
        Renders either a full page or a partial template depending on request type.

        Behavior:
        - HTMX requests return lightweight partial templates for dynamic updates
        - Template selection is based on whether a project status filter is applied
        - Standard requests fall back to the default ListView rendering
        """
        if self.request.headers.get("HX-Request"):
            status = self.request.GET.get("project_status")
            htmx_response = (
                "collaborations/partials/_project-list-wrapper.html"
                if status else
                "collaborations/partials/_gig-cards.html"
            )
            # print(context.get("page_obj").next_page_number)
            # htmx_response = "collaborations/partials/_project-list-wrapper.html"
            
            return render(self.request, htmx_response, context)
        
        return super().render_to_response(context, **response_kwargs)


