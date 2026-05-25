from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, DecimalField, Exists, F, OuterRef, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from collaboration.models.choices import ProjectStatus, ProjectVisibility
from ..models.choices import ProposalStatus
from ..domain.exceptions import ProposalError
from ..application.services import ProposalSubmissionService, ProposalTransitionService
from ..application.dto.modify_proposal_state import ModifyProposalState
from core.model_registry import registry
from core.url_names import ContractURLS
from template_map.proposals import Proposals as ProposalTemplates
from decimal import Decimal
from pydantic import ValidationError
from formatters.pydantic_formatter import format_pydantic_errors


ProposalModel = registry.Proposal
ProposalRoleModel = registry.ProposalRole

    
class RecievedProposalListView(LoginRequiredMixin, ListView):
    template_name = ProposalTemplates.RECEIVED_PROPOSALS
    context_object_name = "gigs"
    paginate_by = 7
    model = registry.Gig

    def get_queryset(self):
        
        active_proposals = ProposalModel.objects.exclude(
            status=ProposalStatus.WITHDRAWN
        )

        proposal_exists = active_proposals.filter(
            project=OuterRef("pk")
        )
        
        base_qs = (
            super()
            .get_queryset()
            .filter(
                creator=self.request.user,
                status=ProjectStatus.PUBLISHED,
                visibility=ProjectVisibility.PUBLIC,
                is_gig_active=True,
            )
        )

        gigs = (
            base_qs
            .annotate(
                total_proposals=Count(
                    "proposals",
                    filter=~Q(proposals__status=ProposalStatus.WITHDRAWN)
                )
            )
            .annotate(
                has_proposals=Exists(proposal_exists)
            )
            .filter(has_proposals=True)
            .order_by("-created_at")
        )

        proposal_status = self.request.GET.get("proposal_status")

        if proposal_status:
            gigs = (
                gigs
                .filter(proposals__status=proposal_status)
                .exclude(proposals__status=ProposalStatus.WITHDRAWN)
                .distinct()
            )
        return gigs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        gig_filter = Q(
            creator=self.request.user,
            status=ProjectStatus.PUBLISHED,
            is_gig_active=True,
        )

        proposal_exists = ProposalModel.objects.exclude(
            status=ProposalStatus.WITHDRAWN
        ).filter(
            project=OuterRef("pk")
        )

        total_budget = (
            self.model.objects.filter(gig_filter)
            .annotate(has_proposals=Exists(proposal_exists))
            .filter(has_proposals=True)
            .aggregate(total=Coalesce(Sum("total_budget"), Decimal("0.00")))["total"]
        )

        proposal_filter = Q(
            proposal__project__creator=self.request.user,
            proposal__project__status=ProjectStatus.PUBLISHED,
            proposal__project__visibility=ProjectVisibility.PUBLIC,
            proposal__project__is_gig_active=True,
        ) & ~Q(
            proposal__status=ProposalStatus.WITHDRAWN
        )

        metrics = ProposalRoleModel.objects.filter(proposal_filter).aggregate(
            # negotiating_worth=Coalesce(
            #     Sum("client_budget", filter=Q(proposal__project__is_negotiable=True)),
            #     Decimal("0.00"),
            # ),
            bid_worth=Coalesce(
                Sum("proposed_amount", filter=Q(proposal__project__is_negotiable=False)),
                Decimal("0.00"),
            ),
        )

        context.update(metrics, gig_total_budget=total_budget)
        return context


class SentProposalListView(LoginRequiredMixin, ListView):
    """
    Renders a paginated list of proposals sent by the currently authenticated user.

    This view fetches all `ProposalModel` instances where the logged-in user is 
    the provider. It optimizes database performance by leveraging select_related 
    and prefetch_related to prevent N+1 query issues, annotates aggregate data 
    directly from the database, and uses deferred loading to only fetch required fields.

    Attributes:
        template_name (str): The path to the template used to render the list.
        context_object_name (str): The variable name used to access the list 
            within the template context ('proposals').
        paginate_by (int): The number of proposals displayed per page (7).
        model (Model): The Django model associated with this list view (ProposalModel).
    """
    template_name = ProposalTemplates.SENT_PROPOSALS
    context_object_name = "proposals"
    paginate_by = 7
    model = ProposalModel

    def get_queryset(self):
        status_filter = self.request.GET.get("status", "").strip().lower()
        qs = (
            super().get_queryset()
            .filter(provider=self.request.user)
            .select_related("project")
            .prefetch_related("roles")
            .only(
                "id",
                "status",
                "sent_at",
                "project__title",
            )
            .order_by("-sent_at")
        )
        self.unfiltered_user_qs = qs
        if status_filter:
            qs = qs.filter(roles__status=status_filter).distinct()

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_status"] = self.request.GET.get("status", "").strip().lower()

        counts = self.unfiltered_user_qs.aggregate(
            total_accepted=Count("id", filter=Q(roles__status="accepted"), distinct=True),
            total_reviewed=Count("id", filter=Q(roles__status="reviewed"), distinct=True),
            total_withdrawn=Count("id", filter=Q(roles__status="withdrawn"), distinct=True),
        )

        context["accepted_count"] = counts["total_accepted"] or 0
        context["reviewed_count"] = counts["total_reviewed"] or 0
        context["withdrawn_count"] = counts["total_withdrawn"] or 0

        return context
    
    
class UpdateProposalStateView(LoginRequiredMixin, View):
    """Updates the state of a service provider proposal"""
    
    allowed_http_names = ["PATCH"]
    
    def patch(self, request:HttpRequest, *args:tuple, **kwrags:dict) -> HttpResponse:
        try:
            data = ModifyProposalState.model_validate_json(request.body)
            ProposalTransitionService(self.request.user, request).modify_state(data)
            resp = {
                "status": "success",
                "title": f"Proposal {data.state.title()}",
                "message": f"The proposal has been {data.state} and the service provider has been notified.",
            }
            if data.state == ProposalStatus.ACCEPTED:
                resp.update(
                    url=reverse_lazy(
                        ContractURLS.PREVIEW_CONTRACT,
                        kwargs={'proposal_id': data.proposal_id, 'role_id': data.role_id}
                    ),
                    redirect=True
                )   
            return JsonResponse(resp, status=200)
        
        except ValidationError as err:
            
            return JsonResponse(
                {
                    "title": "Invalid Data Format",
                    "message": "It looks like some of the information provided doesn't match our requirements. Please check your details and try again.",
                    "status": "error",
                    "feilds": format_pydantic_errors(err)
                },
                status=400,
            )
            
        except ProposalError as err:
            status_code = 400
            data = {
                "title": err.title,
                "message": err.message,
                "status": "error"
            }

            if err.redirect_url:
                status_code = 402
                data.update({
                    "redirect": True,
                    "url": err.redirect_url
                })

            return JsonResponse(data, status=status_code)
            
        except Exception:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                    "title": "System Glitch",
                    "message": "We encountered an unexpected hiccup. Please try again shortly!",
                    "status": "error",
                }, status=500)
    