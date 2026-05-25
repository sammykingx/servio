from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from core.model_registry import registry
from core.url_names import CollaborationURLS
from proposals.models.choices import ProposalStatus
from template_map.proposals import Proposals as ProposalTemplates



class ProposalRoleListView(LoginRequiredMixin, ListView):
    template_name = ProposalTemplates.PROJECT_PROPOSAL_LIST
    context_object_name = "applications"
    paginate_by = 18
    model = registry.Proposal

    def dispatch(self, request, *args, **kwargs):
        """
        Handles invalid or unauthorized access gracefully.

        If the requested project does not exist or does not belong to the user,
        the request is redirected to the collaboration list view instead of
        raising a 404 error.
        """
        project_slug = kwargs.get("project_slug")
        Proposal = self.model

        proposal_exists = Proposal.objects.filter(
            project__slug=project_slug, project__creator=request.user
        ).exclude(status=ProposalStatus.WITHDRAWN).exists()

        if not proposal_exists:
            return redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        project_slug = self.kwargs.get("project_slug")
        proposal_status = self.request.GET.get("proposal_status")

        ProposalRole = registry.ProposalRole

        qs = (
            super()
            .get_queryset()
            .filter(project__slug=project_slug, project__creator=self.request.user)
            .exclude(status=ProposalStatus.WITHDRAWN)
            .select_related("provider", "provider__profile")
            .prefetch_related(
                Prefetch(
                    "roles",
                    queryset=ProposalRole.objects.only(
                        "proposal_id",
                        "client_budget",
                        "proposed_amount",
                        "payment_plan",
                    ),
                )
            )
            .only(
                "id",
                "status",
                "sent_at",
                "provider__first_name",
                "provider__last_name",
                "provider__profile__headline",
                "provider__profile__avatar_url",
            )
            .order_by("-sent_at")
        )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._fetch_project()
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

    def _fetch_project(self):
        project_slug = self.kwargs.get("project_slug")
        GigModel = registry.Gig
        gig_obj = GigModel.objects.only(
            "title", "total_budget", "start_date", "end_date"
        ).get(slug=project_slug)
        return gig_obj
