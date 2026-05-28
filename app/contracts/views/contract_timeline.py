from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView
from template_map.contracts import Contract as ContractTemplates
from core.model_registry import registry
from core.url_names import ContractURLS


class ContractTimelineView(LoginRequiredMixin, DetailView):
    model = registry.Contract
    template_name = ContractTemplates.CONTRACT_TIMELINE
    context_object_name = "contract"
    slug_url_kwarg = "contract_slug"
    
    def get_queryset(self):
        """
        Enforces ownership at the database layer. Only returns a contract 
        if the logged-in user is explicitly the client or the provider.
        """
        user = self.request.user
        return (
            super().get_queryset()
            .filter(Q(client=user) | Q(provider=user))
            .select_related("client", "provider")
        )
        
    def dispatch(self, request, *args, **kwargs):
        """
        Intercepts the request lifecycle early. If get_object() fails due to 
        the queryset filter constraints, cleanly redirects the user back.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(ContractURLS.LIST_CONTRACTS)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract = self.object
        events_log = []

        events_log.append({
            "title": "Contract Created",
            "timestamp": contract.created_at,
            "icon": "description",
            "color": "sky",
            "desc": "Contract terms initiated and drafted into the registry tracking module."
        })

        if contract.client_accepted_terms_at:
            events_log.append({
                "title": "Terms Signed by Client",
                "timestamp": contract.client_accepted_terms_at,
                "icon": "draw",
                "color": "indigo",
                "desc": f"Client ({contract.client.get_full_name().title()}) formally reviewed and executed legal terms."
            })

        if contract.provider_accepted_terms_at:
            events_log.append({
                "title": "Terms Signed by Provider",
                "timestamp": contract.provider_accepted_terms_at,
                "icon": "history_edu",
                "color": "teal",
                "desc": f"Provider ({contract.provider.get_full_name().title()}) counter-signed terms, confirming work availability."
            })

        if contract.client_paid_at:
            events_log.append({
                "title": "Escrow Funded Successfully",
                "timestamp": contract.client_paid_at,
                "icon": "payments",
                "color": "emerald",
                "desc": "Project funding safely deposited and held in smart-escrow storage protection."
            })

        if contract.completed_at:
            events_log.append({
                "title": "Contract Marked Completed",
                "timestamp": contract.completed_at,
                "icon": "verified",
                "color": "purple",
                "desc": "Deliverables confirmed complete. Milestone settlement finalized and released."
            })

        events_log.sort(key=lambda x: x["timestamp"])

        context["timeline_events"] = events_log
        return context
        