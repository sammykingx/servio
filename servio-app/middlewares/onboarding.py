from django.shortcuts import redirect
from django.urls import resolve, reverse_lazy
from accounts.onboarding.manager  import resolve_onboarding_manager
from core.url_names import OnboardingURLS

ONBOARDING_NAMESPACES = {
    OnboardingURLS.Users.APP_NAME,
    OnboardingURLS.Providers.APP_NAME
}

class OnboardingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if not user.is_authenticated:
            return self.get_response(request)

        manager = resolve_onboarding_manager(user)
        if not manager or manager.is_complete():
            return self.get_response(request)
        
        resolver = resolve(request.path_info)
        if resolver.app_name not in ONBOARDING_NAMESPACES:
            return redirect(manager.next_step())

        return self.get_response(request)
