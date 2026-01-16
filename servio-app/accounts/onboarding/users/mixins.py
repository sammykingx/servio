from django.shortcuts import redirect
from ..manager import resolve_onboarding_manager

class OnboardingStepMixin:
    step = None  # required

    def dispatch(self, request, *args, **kwargs):
        manager = resolve_onboarding_manager(request.user)

        if manager and manager.current_step() != self.step:
            return redirect(manager.current_step_url())

        return super().dispatch(request, *args, **kwargs)
