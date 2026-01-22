from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from template_map.collaboration import Collabs


class NegotiationListView(LoginRequiredMixin, ListView):
    template_name = Collabs.LIST_COLLABORATIONS
    context_object_name = "negotiations"
    paginate_by = 8