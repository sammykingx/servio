from django.apps import apps
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Prefetch
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.url_names import CollaborationURLS
from template_map.collaboration import Collabs


GigModel = apps.get_model("collaboration","Gig")
GigRoleModel = apps.get_model("collaboration", "GigRole")
GigApplicationModel = apps.get_model("collaboration", "GigApplication")


class GigDetailView(LoginRequiredMixin, DetailView):
    model = GigModel
    template_name = Collabs.DETAILS
    context_object_name = "gig"
    slug_field = "id"
    slug_url_kwarg = "gig_id"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["editable_statuses"] = ["pending", "draft"]

        return context

    def get_queryset(self):
        return (
            GigModel.objects
            .filter(creator=self.request.user)
            .select_related("creator")
            .prefetch_related(
                Prefetch(
                    "required_roles",
                    queryset=GigRoleModel.objects
                    .select_related("niche")
                    .prefetch_related(
                        Prefetch(
                            "applications",
                            queryset=GigApplicationModel.objects.select_related("user"),
                        )
                    )
                )
            )
        )
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS))
        

class GigPublicDetailView(LoginRequiredMixin, DetailView):
    "for public users interfacing"
    pass


class GigOwnerDetailView(LoginRequiredMixin,DetailView):
    "Creator (see all applications)"
    pass


class GigRoleDetailView(LoginRequiredMixin, DetailView):
    "Role-specific management"
    pass
