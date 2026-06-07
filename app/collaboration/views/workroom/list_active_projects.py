from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q, Sum
from django.views.generic import ListView

from contracts.models.contract import ContractStatus
from core.model_registry import registry
from template_map.collaboration import Collabs


Contract = registry.Contract

class ActivatedProjectContractView(LoginRequiredMixin, ListView):
    template_name = Collabs.Workforce.OVERVIEW
    model = registry.Gig
    context_object_name = "projects"
    
    
    def get_queryset(self):
        user = self.request.user
        
        # Prefetch ALL contracts for the project so the UI can build the complete team stack,
        # regardless of who is viewing it.
        contracts_prefetch = Prefetch(
            'contracts',
            queryset=Contract.objects.select_related('provider').only(
                'id', 'project_id', 'provider__email', 'provider__first_name', 'provider__last_name', 'status'
            ),
            to_attr='all_contracts'
        )

        role_filter = Q(contracts__provider=user, contracts__status=ContractStatus.ACTIVATED) | \
                      Q(contracts__client=user, contracts__status=ContractStatus.ACTIVATED)

        return super().get_queryset().filter(role_filter).distinct().annotate(
            total_combined_value=Sum('contracts__agreed_amount'),
            total_team_size=Count('contracts')
        ).prefetch_related(contracts_prefetch).order_by('-created_at')
        