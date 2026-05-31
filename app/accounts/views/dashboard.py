from django.db.models import Count, Sum, Q, F, Case, When, Value, CharField
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.views.generic import TemplateView
from accounts.models.profile import UserRole
from accounts.models.address import AddressType
from template_map.accounts import Accounts
from core.model_registry import registry
from contracts.models.contract import ContractStatus
from proposals.models.choices import ProposalStatus
from collaboration.models.choices import ProjectStatus


Contract = registry.Contract
Gig = registry.Gig
Payment = registry.Payment
Proposal = registry.Proposal

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = Accounts.Dashboards.MEMBERS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # ---------------------------------------------------------------------
        # 1. METRICS & LIFECYCLE FUNNEL (Aggregated Contract Scan)
        # ---------------------------------------------------------------------
        contract_metrics = Contract.objects.filter(
            Q(client=user) | Q(provider=user)
        ).aggregate(
            # Combined dashboard active count
            total_active=Count('id', filter=Q(status__in=[ContractStatus.SIGNED, ContractStatus.FUNDED])),
            
            # Outbound Escrow: Client committed funds
            funded_contracts=Sum('agreed_amount', filter=Q(client=user, status=ContractStatus.FUNDED)),
            
            # Inbound Escrow: Provider guaranteed earning pipeline
            secured_income=Sum('agreed_amount', filter=Q(provider=user, status=ContractStatus.FUNDED)),
            
            # Pipeline Volumes: Contracts created but not yet fully operationalized
            pipeline_client=Sum('agreed_amount', filter=Q(client=user, status__in=[ContractStatus.AWAITING, ContractStatus.SIGNED])),
            pipeline_provider=Sum('agreed_amount', filter=Q(provider=user, status__in=[ContractStatus.AWAITING, ContractStatus.SIGNED])),
            
            # Segmented Funnel Distribution Counts
            count_awaiting=Count('id', filter=Q(status=ContractStatus.AWAITING)),
            count_signed=Count('id', filter=Q(status=ContractStatus.SIGNED)),
            count_funded=Count('id', filter=Q(status=ContractStatus.FUNDED)),
            count_disputed=Count('id', filter=Q(status=ContractStatus.DISPUTED)),
        )

        # Fallbacks for empty querysets (None -> 0)
        escrow_out = contract_metrics['funded_contracts'] or 0
        escrow_in = contract_metrics['secured_income'] or 0
        pipe_client = contract_metrics['pipeline_client'] or 0
        pipe_provider = contract_metrics['pipeline_provider'] or 0

        context['funded_contracts'] = escrow_out
        context['secured_income'] = escrow_in
        context['active_contracts_count'] = contract_metrics['total_active'] or 0
        context['pipeline_value'] = pipe_client + pipe_provider

        # Contract Lifecycle Funnel Breakdown (for visual funnel component)
        context['funnel'] = {
            'awaiting': contract_metrics['count_awaiting'] or 0,
            'signed': contract_metrics['count_signed'] or 0,
            'funded': contract_metrics['count_funded'] or 0,
            'disputed': contract_metrics['count_disputed'] or 0,
        }

        # ---------------------------------------------------------------------
        # 2. OPERATIONAL PRIORITY QUEUE (Bottlenecks)
        # ---------------------------------------------------------------------
        # Fetch contracts requiring immediate intervention, annotated with user context
        context['priority_items'] = Contract.objects.filter(
            Q(client=user) | Q(provider=user),
            status__in=[ContractStatus.AWAITING, ContractStatus.SIGNED, ContractStatus.DISPUTED]
        ).annotate(
            user_role=Case(
                When(client=user, then=Value('client')),
                When(provider=user, then=Value('provider')),
                output_field=CharField(),
            )
        ).select_related('project', 'client', 'provider').order_by(
            # Pushes Disputed to the top, followed by Awaiting Signatures
            Case(
                When(status=ContractStatus.DISPUTED, then=Value(1)),
                When(status=ContractStatus.AWAITING, then=Value(2)),
                When(status=ContractStatus.SIGNED, then=Value(3)),
                default=Value(4),
                output_field=CharField(),
            )
        )

        # ---------------------------------------------------------------------
        # 3. OPEN OPPORTUNITIES / INCOMING PROPOSALS
        # ---------------------------------------------------------------------
        # Fetch client's gigs that have pending proposals waiting to be accepted/rejected
        context['pending_proposals_gigs'] = Gig.objects.filter(
            creator=user,
            status=ProjectStatus.PUBLISHED, # Or your specific ProjectStatus choice matching active marketplace listings
            proposals__status=ProposalStatus.SENT # Look for incoming unreviewed proposals
        ).annotate(
            pending_count=Count('proposals', filter=Q(proposals__status=ProposalStatus.SENT))
        ).filter(pending_count__gt=0)

        # ---------------------------------------------------------------------
        # 4. RECENT PLATFORM PAYMENTS (Gateway Ledger Tracking)
        # ---------------------------------------------------------------------
        # Querying payments ledger for recent activity involving this user
        context['recent_payments'] = Payment.objects.filter(
            Q(user=user) | Q(beneficiary=user)
        ).order_by('-created_at')[:5]

        # ---------------------------------------------------------------------
        # 5. POST-FUNDING HAND-OFF CONTEXT (WhatsApp/Email Bridge)
        # ---------------------------------------------------------------------
        # Show recent handoff if a contract was funded within the past 48 hours
        time_threshold = timezone.now() - timedelta(hours=48)
        latest_funded_handoff = Contract.objects.filter(
            Q(client=user) | Q(provider=user),
            status=ContractStatus.FUNDED,
            client_paid_at__gte=time_threshold
        ).select_related('client', 'provider', 'project').order_by('-client_paid_at').first()

        context['handoff'] = None
        if latest_funded_handoff:
            is_client = (latest_funded_handoff.client == user)
            partner = latest_funded_handoff.provider if is_client else latest_funded_handoff.client
            context['handoff'] = {
                'contract': latest_funded_handoff,
                'is_client': is_client,
                'partner_name': partner.get_full_name() or partner.email,
                'partner_email': partner.email,
                # Fallback profile check assuming profile phone fields exist
                'partner_phone': getattr(getattr(partner, 'profile', None), 'phone', ''), 
            }
            
        context['has_gig'] = Gig.objects.filter(creator=user).exists()

        return context
    # def get_template_names(self):
    #     user = self.request.user
    #     role = getattr(user.profile, "role", UserRole.MEMBERS)

    #     template_map = {
    #         UserRole.ADMIN: Accounts.Dashboards.ADMIN,
    #         UserRole.MEMBERS: Accounts.Dashboards.MEMBERS,
    #         UserRole.PROVIDERS: Accounts.Dashboards.PROVIDERS,
    #         UserRole.STAFF: Accounts.Dashboards.STAFFS,
    #     }

    #     # if user.is_verified is False:
    #     #     messages.warning(
    #     #         self.request,
    #     #         "Please verify your email to access all features.",
    #     #         extra_tags="Email Not Verified",
    #     #     )
    #     # Return template based on role, fallback to default
    #     return [template_map.get(role, self.template_name)]
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["gigs"] = self.fetch_gig_info()
    #     context["proposals"] = self.fetch_recent_proposals()
    #     context["recent_payments"] = self.fetch_recent_payments()
    #     user = self.request.user

    #     if not user.is_verified:
    #         context["toast"] = {
    #             "message": "Go to Profile > Security & Trust to verify your email and access all features.",
    #             "type": "warning",
    #             "title": "Email Not Verified",
    #         }

    #     return context
    
    # def fetch_gig_info(self):
    #     return (
    #         self.request.user.gigs
    #         .prefetch_related("required_roles")
    #         .annotate(
    #             role_count_db=Count("required_roles"),
    #             total_role_budget_db=Sum(
    #                 F("required_roles__budget") * F("required_roles__slots")
    #             ),
    #         )
    #         .order_by("-created_at")[:3]
    #     )
        
    # def fetch_recent_proposals(self):
    #     ProposalModel = registry.Proposal
    #     return (
    #         ProposalModel.objects
    #         .filter(project__creator=self.request.user)
    #         .select_related("provider", "project")
    #         # .only(
    #         #     "id",
    #         #     "status",
    #         #     "sent_at",
    #         #     "gig__title",
    #         #     "sender__id",
    #         #     "sender__username",
    #         # )
    #         .order_by("-created_at")[:4]
    #     )
    
    # def fetch_recent_payments(self):
    #     PaymentModel = registry.Payment
    #     return (
    #         PaymentModel.objects
    #         .filter(user=self.request.user)
    #         .select_related("beneficiary")
    #         .order_by("-created_at")[:3]
    #     )


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's profile page.
    """

    template_name = Accounts.ACCOUNT_PROFILE

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        addresses = self.request.user.addresses
        ctx["social_links"] = {
            link.platform: link.url
            for link in self.request.user.social_links.all()
        }

        ctx["home"] = addresses.filter(label=AddressType.HOME).first()
        return ctx
