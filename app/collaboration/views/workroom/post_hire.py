from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q, Sum
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from contracts.models.contract import ContractStatus
from core.model_registry import registry
from core.url_names import WorkroomURLS
from template_map.collaboration import Collabs

import urllib


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
    template_name = Collabs.Workforce.PROJECT_WORKROOM
    model = registry.Gig
    context_object_name = "project"
    

    def dispatch(self, request:HttpRequest, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        is_owner = self.object.creator == user

        is_provider = Contract.objects.filter(
            project=self.object,
            provider=user,
            provider_accepted_terms_at__isnull=False
        ).exists()

        if not (is_owner or is_provider):
            return redirect(reverse(WorkroomURLS.OVERVIEW))

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contracts = Contract.objects.filter(
            project=self.object,
            provider_accepted_terms_at__isnull=False
        ).select_related(
            'provider', 
            'provider__profile', 
            'proposal_role'
        ).prefetch_related(
            'proposal_role__deliverables'
        )

        context['contracts'] = contracts
        return context
