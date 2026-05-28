from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import ListView
from core.model_registry import registry
from template_map.contracts import Contract as ContractTemplates



class ContractListView(LoginRequiredMixin, ListView):
    model = registry.Contract
    template_name = ContractTemplates.LIST_CONTRACTS
    context_object_name = "contracts"
    paginate_by = 10  # Built-in pagination matches your template page iteration

    def get_queryset(self):
        """
        Returns the top contracts involving the current logged-in user.
        Optimized with select_related to prevent N+1 issues when pulling profile info.
        """
        user = self.request.user
        return (
            super().get_queryset()
            .filter(Q(client=user) | Q(provider=user))
            .select_related("client", "provider")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        """
        Injects conditional aggregates into the template stats context matching 
        the exact structural layout designed in our UI step.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        stats = (
            self.model.objects.filter(Q(client=user) | Q(provider=user))
            .aggregate(
                all_count=Count("id"),
                completed_count=Count(
                    "id", 
                    filter=Q(status="completed")
                ),
                pending_count=Count(
                    "id", 
                    filter=Q(status__in=["awaiting", "signed", "funded"])
                ),
                
                disputed_or_cancelled_count=Count(
                    "id", 
                    filter=Q(status__in=["cancelled", "disputed"])
                ),
            )
        )

        context["stats"] = {
            "all": stats["all_count"],
            "completed": stats["completed_count"],
            "pending": stats["pending_count"],
            "disputed_or_cancelled": stats["disputed_or_cancelled_count"],
        }
        
        return context