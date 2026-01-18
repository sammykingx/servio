from django.shortcuts import redirect
from ..manager import resolve_onboarding_manager

class OnboardingStepMixin:
    view_step = None

    def dispatch(self, request, *args, **kwargs):
        manager = resolve_onboarding_manager(request.user)
        if self.view_step > manager.user_step:
            return redirect(manager.next_step_url())
        
        if request.method == "POST" and self.view_step < manager.user_step:
            return redirect(manager.next_step_url())

        return super().dispatch(request, *args, **kwargs)
