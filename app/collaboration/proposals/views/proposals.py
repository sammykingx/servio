from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, DecimalField, Exists, F, OuterRef, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, View
from collaboration.models.choices import GigStatus, GigVisibility, ProposalStatus
from collaboration.proposals.exceptions import ProposalError
from collaboration.proposals.services import ProposalService
from template_map.collaboration import Collabs
from registry_utils import get_registered_model
from decimal import Decimal


class RecievedProposalListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Proposals.RECEIVED_PROPOSALS
    context_object_name = "gigs"
    paginate_by = 7
    model = get_registered_model("collaboration", "Gig")

    def get_queryset(self):
        Proposal = get_registered_model("collaboration", "Proposal")
        proposals = Proposal.objects.filter(gig=OuterRef("pk"))
        base_qs = (
            super()
            .get_queryset()
            .filter(
                creator=self.request.user,
                status=GigStatus.PUBLISHED,
                visibility=GigVisibility.PUBLIC,
                is_gig_active=True,
            )
        )

        gigs = (
            base_qs.annotate(total_proposals=Count("proposals"))
            .annotate(has_proposals=Exists(proposals))
            # .annotate(latest_proposal_date=Max("proposals__created_at"))
            .filter(has_proposals=True)
            .order_by("created_at")
            # .order_by("-latest_proposal_date")
        )

        proposal_status = self.request.GET.get("proposal_status")

        if proposal_status:
            base_qs = base_qs.filter(proposals__status=proposal_status).distinct()

        return gigs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        Proposal = get_registered_model("collaboration", "Proposal")
        ProposalRole = get_registered_model("collaboration", "ProposalRole")

        gig_filter = Q(
            creator=self.request.user,
            status=GigStatus.PUBLISHED,
            is_gig_active=True,
        )

        proposal_exists = Proposal.objects.filter(gig=OuterRef("pk"))

        total_budget = (
            self.model.objects.filter(gig_filter)
            .annotate(has_proposals=Exists(proposal_exists))
            .filter(has_proposals=True)
            .aggregate(total=Coalesce(Sum("total_budget"), Decimal("0.00")))["total"]
        )

        proposal_filter = Q(
            proposal__gig__creator=self.request.user,
            proposal__gig__status=GigStatus.PUBLISHED,
            proposal__gig__visibility=GigVisibility.PUBLIC,
            proposal__gig__is_gig_active=True,
        )

        metrics = ProposalRole.objects.filter(proposal_filter).aggregate(
            negotiating_worth=Coalesce(
                Sum("proposed_amount", filter=Q(proposal__is_negotiating=True)),
                Decimal("0.00"),
            ),
            accepted_worth=Coalesce(
                Sum("role_amount", filter=Q(proposal__is_negotiating=False)),
                Decimal("0.00"),
            ),
        )

        context.update(metrics, gig_total_budget=total_budget)
        return context

class SentProposalListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Proposals.SENT_PROPOSALS
    context_object_name = "proposals"
    paginate_by = 7
    model = get_registered_model("collaboration", "Proposal")

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(sender=self.request.user)
            .select_related(
                "gig",
            )
            .prefetch_related("roles")
            .annotate(
                role_count=Count("roles"),
                total_proposed=Coalesce(
                    Sum("roles__proposed_amount"),
                    0,
                    output_field=DecimalField(),
                ),
            )
            .only(
                "id",
                "status",
                "is_negotiating",
                "sent_at",
                "gig__title",
                "gig__total_budget",
                "gig__slug",
            )
            .order_by("-sent_at")
        )
        return qs
    
class UpdateProposalStatusView(LoginRequiredMixin, View):
    """Accepts service provider proposal"""
    
    allowed_http_names = ["PATCH"]
    
    def patch(self, request, *args, **kwrags) -> HttpResponse:
        state = request.GET.get("state")
        proposal_id = request.GET.get("proposal_id")
        proposal_role_id = request.GET.get("proposal_role_id")
        
        allowed_states = {
            ProposalStatus.ACCEPTED, 
            ProposalStatus.REJECTED, 
            ProposalStatus.WITHDRAWN
        }
        
        if state not in allowed_states:
            return JsonResponse({
                "error": "Unkown State",
                "message": "Sorry! the state processed isn't on the guest list for this proposal right now.",
                "status": "error"
            }, status=400)
        
        try:
            proposal_service = ProposalService(self.request.user, request)
            self.update_proposal_state(proposal_service, state)
            
        except ProposalError as err:
            return JsonResponse({
                "error": err.title,
                "message": err.message,
                "status": "error"
            }, status=400)
            
        except Exception:
            return JsonResponse({
                    "error": "System Glitch",
                    "message": "We encountered an unexpected hiccup. Please try again shortly!",
                    "status": "error",
                }, status=500)
        
        return JsonResponse({
            "status": "success",
            "title": f"Proposal {state.title()}",
            "message": f"The proposal has been {state} and the service provider has been notified."
        }, status=200)
        
    def update_proposal_state(self, service: ProposalService, state:str):
        if not isinstance(service, ProposalService):
            raise Exception("proposal_service must be an instance of ProposalService")
        
        print(f"State received: {state}")
        import time
        time.sleep(5)
        # if state == ProposalStatus.ACCEPTED:
        #     service.accept_proposals("proposal obj", "proposal role_obj")
            
    