from django.apps import apps
from django.shortcuts import render
from django.db.models import Count, Sum, F, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from collaboration.models.choices import GigStatus, GigVisibility, RoleStatus
from template_map.collaboration import Collabs

GigsModel = apps.get_model("collaboration", "Gig")
GigRole = apps.get_model("collaboration", "GigRole")

class OppurtunityListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Oppurtunities.LIST
    context_object_name = "gigs"
    paginate_by = 4

    def get_queryset(self):
        user = self.request.user
        profile = user.profile

        industry = profile.industry
        niches = profile.niches.all()

        # Base public gigs
        base_qs = (
            GigsModel.objects
            .filter(
                status=GigStatus.PENDING,
                visibility=GigVisibility.PUBLIC,
                is_gig_active=True,
            )
        )

        # Return None preferences → show nothing (or fallback logic)
        if not industry and not niches.exists():
            return base_qs.none()

        # Role-based gig filtering
        role_match_q = Q()

        if niches.exists():
            role_match_q |= Q(required_roles__niche__in=niches)

        if industry:
            role_match_q |= Q(required_roles__niche__parent=industry)

        gigs = (
            base_qs
            .filter(role_match_q)
            .distinct()
        )

        # Prefetch ONLY relevant roles
        role_filters = Q(status=RoleStatus.OPEN)

        if niches.exists():
            role_filters &= Q(niche__in=niches)

        if industry:
            role_filters |= Q(niche__parent=industry)

        matching_roles_qs = (
            GigRole.objects
            .filter(role_filters)
            .select_related("niche")
        )

        gigs = gigs.prefetch_related(
            Prefetch(
                "required_roles",
                queryset=matching_roles_qs,
                to_attr="matched_roles"
            )
        )

        return gigs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request"):
            htmx_response = None
            return render(self.request, htmx_response, context)
        
        return super().render_to_response(context, **response_kwargs)


