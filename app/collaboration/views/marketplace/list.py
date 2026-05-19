from django.shortcuts import render
from django.db.models import Exists, Q, OuterRef, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from core.model_registry import registry
from collaboration.models.choices import ProjectStatus, ProjectVisibility, ProjectRoleStatus
from template_map.collaboration import Collabs


GigsModel = registry.Gig
GigRole = registry.GigRole
Proposal = registry.Proposal


class OppurtunityListView(LoginRequiredMixin, ListView):
    """
        Displays a curated list of publicly available collaboration opportunities
        tailored to the authenticated user's industry and niche skill set.

        The view prioritizes projects that:
        - Are published, active, and publicly visible
        - Were not created by the current user
        - Either require no specific roles or contain roles that match the user's niches

        Each project is enriched with matching metadata (match count, percentage, budget
        range, priority label) to improve relevance ranking and presentation.
    """
    model = GigsModel
    template_name = Collabs.Marketplace.LIST
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        """
        :Description:
            Builds and returns a ranked list of projects based on how well they match
            the user's industry and niche skills.

            :Matching logic:
                - projects without required roles are included as open opportunities
                - projects with required roles are included only if at least one role
            matches the user's niches within their industry

            **For each project, the method calculates:**
                - Number of matched roles
                - Match percentage against user's niches
                - Budget range derived from matched roles
                - Display-friendly description and budget
                - Priority score and label used for sorting

            Returns:
                list: A sorted list of project objects ordered by priority and match strength.
        """
        user = self.request.user
        profile = user.profile
        user_industry_id = profile.industry_id
        user_niches = profile.get_user_niches
        user_niche_count = len(user_niches)
        
        user_proposals = Proposal.objects.filter(
            project=OuterRef("pk"),
            provider=user
        )
        
        base_qs = (
            super().get_queryset()
            .filter(
                status=ProjectStatus.PUBLISHED,
                visibility=ProjectVisibility.PUBLIC,
                is_gig_active=True
            )
            .exclude(creator=user)
            .annotate(
                user_has_proposal=Exists(user_proposals)
            )
            .filter(user_has_proposal=False)
        )

        matched_roles = GigRole.objects.filter(
            status=ProjectRoleStatus.OPEN,
            niche_id=user_industry_id,
            role_id__in=user_niches,
        )

        projects = ( 
            base_qs
            .filter(
                Q(has_gig_roles=False) |
                Q(required_roles__in=matched_roles)
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "required_roles",
                    queryset=matched_roles,
                    to_attr="matched_roles",
                )
            )
        )
        
        user_niche_count = len(user_niches)

        # --------------------------
        # projects meta data
        # --------------------------
        for project in projects:
            matched_roles = getattr(project, "matched_roles", [])

            project.match_count = len(matched_roles)

            # ------------------------------
            # projects WITH matching roles
            # ------------------------------
            if project.match_count > 0:
                project.match_percentage = int(
                    (project.match_count / user_niche_count) * 100
                )

                budgets = [r.budget for r in matched_roles]
                project.min_budget = min(budgets)
                project.max_budget = max(budgets)

                # Description logic
                if project.match_count == 1:
                    project.display_description = matched_roles[0].description
                else:
                    project.display_description = project.description

                # Priority
                if project.match_count == 1:
                    project.priority_score = 3
                    project.priority_label = "High Priority"

                elif project.match_count == user_niche_count:
                    project.priority_score = 3
                    project.priority_label = "High Priority"

                else:
                    project.priority_score = 2
                    project.priority_label = f"{project.match_percentage}% Match"

                # Budget display
                if project.match_count == 1:
                    project.display_budget = project.min_budget
                else:
                    project.display_budget = f"{project.min_budget} – {project.max_budget}"

            # ------------------------------
            # General projects (no roles)
            # ------------------------------
            else:
                project.match_percentage = 0
                project.match_count = 0
                project.priority_score = 1
                project.priority_label = "Open for collaboration"
                project.display_budget = project.total_budget
                project.display_description = project.description

                        
        projects = sorted(
            projects,
            key=lambda g: (
                g.priority_score,
                g.match_count,
            ),
            reverse=True
        )

        return projects
        
    def get_context_data(self, **kwargs):
        """
        Extends the default context for the opportunity list view.

        Currently relies on the base implementation, but exists as an extension
        point for future context enrichment.
        """
        context = super().get_context_data(**kwargs)

        return context
    
    def render_to_response(self, context, **response_kwargs):
        """
        Renders the response differently for HTMX requests.

        - HTMX requests return a partial template for dynamic page updates
        - Standard requests fall back to the default ListView rendering
        """
        if self.request.headers.get("HX-Request"):
            htmx_response = None
            return render(self.request, htmx_response, context)
        
        return super().render_to_response(context, **response_kwargs)


