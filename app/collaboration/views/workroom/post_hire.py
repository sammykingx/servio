from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q, Sum
from django.views.generic import DetailView, ListView

from contracts.models.contract import ContractStatus
from core.model_registry import registry
from template_map.collaboration import Collabs


Contract = registry.Contract

class ContractedProjectListView(LoginRequiredMixin, ListView):
    """
    Displays an overview of active, contracted projects for both clients and providers.

    Filters for projects where the current user has an activated contract, 
    annotating each with total financial value and team size while prefetching 
    optimized contract and counterpart contact details for workroom navigation.
    """
    template_name = Collabs.Workforce.OVERVIEW
    model = registry.Gig
    context_object_name = "projects"
    
    
    def get_queryset(self):
        user = self.request.user
        
        contracts_prefetch = Prefetch(
            'contracts',
            queryset=Contract.objects.select_related('provider').only(
                'id', 'project_id', 'provider__email', 'provider__first_name', 
                'provider__last_name', 'status', 'slug'
            ),
            to_attr='all_contracts'
        )

        role_filter = Q(contracts__provider=user, contracts__status=ContractStatus.ACTIVATED) | \
                      Q(contracts__client=user, contracts__status=ContractStatus.ACTIVATED)

        return super().get_queryset().filter(role_filter).distinct().annotate(
            total_combined_value=Sum('contracts__agreed_amount'),
            total_team_size=Count('contracts')
        ).prefetch_related(contracts_prefetch).order_by('-created_at')
    
    
class ProjectWorkroomDetailView(LoginRequiredMixin, DetailView):
    pass