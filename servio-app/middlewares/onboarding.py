from django.shortcuts import redirect
from django.urls import reverse_lazy
from constants.onboarding_flow import ONBOARDING_FLOWS
from accounts.models.profile import UserRole

class OnboardingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # 1. Anonymous users → normal processing
        if not user.is_authenticated or user.completed_onboarding:
            return self.get_response(request)

        print(request.resolver_match)
        # # Resolver safety (admin, static, etc.)
        # if not request.resolver_match:
        #     return self.get_response(request)

        # current_view = request.resolver_match.view_name

        # # 3. Allow onboarding URLs themselves
        # if current_view.startswith("onboarding."):
        #     return self.get_response(request)

        # # 4. Force into correct onboarding step
        # role = getattr(user.profile, "role", UserRole.MEMBERS)
        # flow = ONBOARDING_FLOWS.get(role)

        # # Defensive guard
        # step = min(user.onboarding_step, len(flow) - 1)
        # required_view = flow[step]

        # return redirect(reverse_lazy(required_view))
        return self.get_response(request)
