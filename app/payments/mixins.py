from django.apps import apps
from django.shortcuts import redirect
from django.urls import reverse_lazy
from core.url_names import CollaborationURLS
from collaboration.models.choices import GigStatus


GigModel = apps.get_model("collaboration","Gig")


class GigPaymentMixin:
    gig = None

    def get_gig_queryset(self):
        return (
            GigModel.objects
            .select_related("creator")
            .prefetch_related("required_roles")
        )

    def get_gig(self):
        return (
            self.get_gig_queryset()
            .filter(
                id=self.kwargs["gig_id"],
                creator=self.request.user,
                status=GigStatus.PENDING,
            )
            .first()
        )

    def dispatch(self, request, *args, **kwargs):
        self.gig = self.get_gig()

        if not self.gig:
            return redirect(
                reverse_lazy(CollaborationURLS.LIST_COLLABORATIONS)
            )

        return super().dispatch(request, *args, **kwargs)

    def get_gig_context(self):
        return {
            "gig": self.gig
        }
