from django.apps import apps
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import render
from django.http.response import HttpResponse
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView, View
from django.views.generic import CreateView
from template_map.collaboration import Collabs
from core.url_names import CollaborationURLS
from ..forms import GigCreateForm, GigRoleFormSet
import json


GigCategory = apps.get_model("collaboration", "GigCategory")

class CreateCollaborationView(LoginRequiredMixin, CreateView):
    """
    Docstring for CreateCollaborationView
    """
    model = apps.get_model("collaboration","Gig")
    
    form_class = GigCreateForm
    template_name = Collabs.CREATE
    success_url = reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["role_formset"] = GigRoleFormSet(self.request.POST)
        else:
            context["role_formset"] = GigRoleFormSet()
        niches = (
            GigCategory.objects
            .filter(parent__isnull=True, is_active=True)
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=GigCategory.objects.filter(is_active=True).order_by("name")
                )
            )
            .order_by("name")
        )

        taxonomy = [
            {
                "id": niche.id,
                "name": niche.name,
                "subcategories": [
                    {
                        "id": sub.id,
                        "name": sub.name,
                    }
                    for sub in niche.subcategories.all()
                ],
            }
            for niche in niches
        ]

        context["gig_taxonomy"] = json.dumps(taxonomy)
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        role_formset = context["role_formset"]

        if not role_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            form.instance.creator = self.request.user
            gig = form.save()

            role_formset.instance = gig
            role_formset.save()

        return super().form_valid(form)
