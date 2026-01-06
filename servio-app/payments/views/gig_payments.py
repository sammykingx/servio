from django.apps import apps
from django.urls import reverse_lazy
from core.url_names import CollaborationURLS
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from template_map.payments import Payments
from collaboration.models.choices import GigStatus


GigModel = apps.get_model("collaboration","Gig")


class GigPaymentView(LoginRequiredMixin, TemplateView):
    template_name = Payments.GigPayments.GIG_OVERVIEW

    def dispatch(self, request, *args, **kwargs):
        self.gig = (
            GigModel.objects
            .select_related("creator")
            .prefetch_related("required_roles")
            .filter(
                id=kwargs["gig_id"],
                creator=request.user,
                status=GigStatus.PENDING
            )
            .first()
        )

        if not self.gig:
            return redirect(reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS))

        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["gig"] = self.gig
        # context["payment_summary"] = {
        #     "title": self.gig.title,
        #     "budget": self.gig.budget,
        #     "currency": self.gig.currency,
        #     "roles": [
        #         {
        #             "niche": role.niche.name,
        #             "professional": role.professional.name,
        #             "budget": role.budget,
        #         }
        #         for role in self.gig.roles.all()
        #     ]
        # }

        return context