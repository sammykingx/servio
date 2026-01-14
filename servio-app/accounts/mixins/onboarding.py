from django.shortcuts import redirect
from django.urls import reverse
from accounts.models.profile import UserRole
from constants.onboarding_flow import ONBOARDING_FLOWS
from typing import Union


class OnboardingRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        current_view = request.resolver_match.view_name

        if user.completed_onboarding:
            return super().dispatch(request, *args, **kwargs)

        required_view = ONBOARDING_FLOWS[UserRole.MEMBERS][user.onboarding_step]
        # User trying to access a later step? → redirect back
        if current_view != required_view:
            return redirect(reverse(required_view))

        return super().dispatch(request, *args, **kwargs)
    
    def get_step_index(self, view_name: str) -> int:
        return ONBOARDING_FLOWS.index(view_name)

    def get_next_step(self, step_index: int) -> str | None:
        try:
            return ONBOARDING_FLOWS[step_index + 1]
        except IndexError:
            return None

