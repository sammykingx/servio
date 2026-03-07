from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, DecimalField, Exists, F, OuterRef, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views.generic import ListView
from collaboration.models.choices import GigStatus, GigVisibility, ProposalStatus
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
