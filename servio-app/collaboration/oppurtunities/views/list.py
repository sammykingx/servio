from django.apps import apps
from django.shortcuts import render
from django.db.models import Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from collaboration.models.choices import GigStatus, GigVisibility, RoleStatus
from template_map.collaboration import Collabs

GigsModel = apps.get_model("collaboration", "Gig")
GigRole = apps.get_model("collaboration", "GigRole")

class OppurtunityListView(LoginRequiredMixin, ListView):
    template_name = Collabs.Oppurtunities.LIST
    context_object_name = "gigs"
    paginate_by = 18

    def get_queryset(self):
        user = self.request.user
        profile = user.profile
        user_industry_id = profile.industry_id
        user_niches = profile.niches.values_list("id", flat=True)
        user_niche_count = len(user_niches)
        
        base_qs = GigsModel.objects.filter(
            status=GigStatus.PENDING,
            visibility=GigVisibility.PUBLIC,
            is_gig_active=True
        ).exclude(creator=user)
        
        matched_roles = GigRole.objects.filter(
            status=RoleStatus.OPEN,
            niche_id=user_industry_id,
            role_id__in=user_niches,
        )

        gigs_without_roles = base_qs.filter(has_gig_roles=False)
        gigs_with_matching_roles = base_qs.filter(
            required_roles__in=matched_roles,
        ).distinct()

        gigs = ( 
            base_qs
            .filter(
                Q(has_gig_roles=False) |
                Q(required_roles__in=matched_roles)
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "required_roles",
                    queryset=matched_roles,
                    to_attr="matched_roles",
                )
            )
        )
        
        user_niche_count = len(user_niches)

        # --------------------------
        # Gigs meta data
        # --------------------------
        for gig in gigs:
            matched_roles = getattr(gig, "matched_roles", [])

            gig.match_count = len(matched_roles)

            # ------------------------------
            # Gigs WITH matching roles
            # ------------------------------
            if gig.match_count > 0:
                gig.match_percentage = int(
                    (gig.match_count / user_niche_count) * 100
                )

                budgets = [r.budget for r in matched_roles]
                gig.min_budget = min(budgets)
                gig.max_budget = max(budgets)

                # Description logic
                if gig.match_count == 1:
                    gig.display_description = matched_roles[0].description
                else:
                    gig.display_description = gig.description

                # Priority
                if gig.match_count == 1:
                    gig.priority_score = 3
                    gig.priority_label = "High Priority"

                elif gig.match_count == user_niche_count:
                    gig.priority_score = 3
                    gig.priority_label = "High Priority"

                else:
                    gig.priority_score = 2
                    gig.priority_label = f"{gig.match_percentage}% Match"

                # Budget display
                if gig.match_count == 1:
                    gig.display_budget = gig.min_budget
                else:
                    gig.display_budget = f"{gig.min_budget} – {gig.max_budget}"

            # ------------------------------
            # General gigs (no roles)
            # ------------------------------
            else:
                gig.match_percentage = 0
                gig.match_count = 0
                gig.priority_score = 1
                gig.priority_label = "Open for collaboration"
                gig.display_budget = gig.total_budget
                gig.display_description = gig.description

                        
        gigs = sorted(
            gigs,
            key=lambda g: (
                g.priority_score,
                g.match_count,
            ),
            reverse=True
        )

        return gigs

        # Build role relevance
        role_match_q = Q(has_gig_roles=False)  # Include general gigs
        # print(f"\nHas gig roles FALSE: {role_match_q}\n")
        # print(base_qs.filter(role_match_q).count())
        
        # if niches.exists():
        #     role_match_q |= Q(
        #         has_gig_roles=True,
        #         required_roles__status=RoleStatus.OPEN,
        #         required_roles__niche__in=niches
        #     )
            
        #     a= Q(
        #         has_gig_roles=True,
        #         required_roles__status=RoleStatus.OPEN,
        #         required_roles__niche__in=niches
        #     )
        #     print(f"\n A => {a}\n")
        #     print(base_qs.filter(a).count())
        
        # # Apply filter
        # gigs = base_qs.filter(role_match_q).distinct()
        # print("gigs: ", gigs.count())

        # # Prefetch only matching roles
        # matching_roles_qs = GigRole.objects.filter(
        #     status=RoleStatus.OPEN,
        #     niche__in=niches
        # ).select_related("niche")

        # gigs = gigs.prefetch_related(
        #     Prefetch(
        #         "required_roles",
        #         queryset=matching_roles_qs,
        #         to_attr="matched_roles"
        #     )
        # )

        return gigs
        # -------------------------------------------
        # Shared role relevance for gigs and roles
        # -------------------------------------------
        # role_match = Q(status=RoleStatus.OPEN)

        # niche_or_industry = Q()
        # if niches.exists():
        #     niche_or_industry |= Q(niche__in=niches)

        # if industry:
        #     niche_or_industry |= Q(niche__parent=industry)

        # role_match &= niche_or_industry

        # print(niche_or_industry)
        # print(role_match)
        # # -------------------------------
        # # Filter gigs via matching roles
        # # -------------------------------
        # gigs = (
        #     base_qs
        #     .filter(required_roles__in=GigRole.objects.filter(role_match))
        #     .distinct()
        # )
        
        # print("Filtered out gigs: ", gigs)

        # # -------------------------------
        # # Prefetch ONLY relevant roles
        # # -------------------------------
        # matching_roles_qs = (
        #     GigRole.objects
        #     .filter(role_match)
        #     .select_related("niche")
        # )

        # gigs = gigs.prefetch_related(
        #     Prefetch(
        #         "required_roles",
        #         queryset=matching_roles_qs,
        #         to_attr="matched_roles",
        #     )
        # )

        # return gigs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request"):
            htmx_response = None
            return render(self.request, htmx_response, context)
        
        return super().render_to_response(context, **response_kwargs)


