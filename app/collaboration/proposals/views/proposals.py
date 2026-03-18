from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, DecimalField, Exists, F, OuterRef, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from collaboration.models.choices import GigStatus, GigVisibility, ProposalStatus
from collaboration.proposals.exceptions import ProposalError
from collaboration.proposals.services import ProposalService
from collaboration.schemas.modify_proposal_state import ModifyProposalState
from core.url_names import CollaborationURLS
from template_map.collaboration import Collabs
from registry_utils import get_registered_model
from decimal import Decimal
from pydantic import ValidationError
from formatters.pydantic_formatter import format_pydantic_errors
import json


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
        try:
            payload = json.loads(request.body)
            data = ModifyProposalState(**payload)
            proposal_service = ProposalService(self.request.user, request)
            self.update_proposal_state(proposal_service, data)
            
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "status": "error",
                    "title": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400,
            )
            
        except ValidationError as err:
            return JsonResponse(
                {
                    "title": "Invalid Data Format",
                    "message": "It looks like some of the information provided doesn't match our requirements. Please check your details and try again.",
                    "status": "error"
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
        
        resp = {
            "status": "success",
            "title": f"Proposal {data.state.title()}",
            "message": f"The proposal has been {data.state} and the service provider has been notified.",
        }
        
        if data.state == ProposalStatus.ACCEPTED:
            resp.update(
                url=reverse_lazy(
                    CollaborationURLS.COMPLETE_COLLABORATION,
                    kwargs={'proposal_id': data.proposal_id}
                ),
                redirect=True
            )
            
        return JsonResponse(resp, status=200)
        
    def update_proposal_state(self, service: ProposalService, data:ModifyProposalState):
        if not isinstance(service, ProposalService):
            raise Exception("proposal_service must be an instance of ProposalService")
        service.modify_proposal_state(data)
            
    