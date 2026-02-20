
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from template_map.collaboration import Collabs
from registry_utils import get_registered_model


class NegotiationListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Proposals.LIST
    context_object_name = "proposals"
    paginate_by = 8
    model = get_registered_model("collaboration", "Proposal")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["negotiations"] = True
        return context