from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.profile import UserRole
from constants.onboarding_flow import ONBOARDING_FLOWS
from typing import Union


class BaseOnboardingView(LoginRequiredMixin):
    """
    Base class for all onboarding steps.
    Handles step progression and completion.
    """

    def get_flow(self, user):
        role = getattr(user.profile, "role", UserRole.MEMBERS)
        return ONBOARDING_FLOWS[role]

    def get_next_step(self, user) -> Union[str, None]:
        flow = self.get_flow(user)
        try:
            return flow[user.onboarding_step + 1]
        except IndexError:
            return None

    def advance_user(self) -> str:
        """
        Call this AFTER successfully processing the current step.
        """
        user = self.request.user
        next_view = self.get_next_step(user)

        # Final step
        if not next_view:
            self.complete_onboarding(user)
            return reverse_lazy("dashboard")

        user.onboarding_step += 1
        user.save(update_fields=["onboarding_step"])

        return reverse_lazy(next_view)

    def complete_onboarding(self, user):
        if not user.onboarding_completed:
            user.onboarding_completed = True
            user.save(update_fields=["onboarding_completed"])
    
