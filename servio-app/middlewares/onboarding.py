from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve
from accounts.onboarding.manager  import resolve_onboarding_manager
from core.url_names import AuthURLNames, OnboardingURLS

ONBOARDING_NAMESPACES = {
    OnboardingURLS.Users.APP_NAME,
    OnboardingURLS.Providers.APP_NAME
}

ONBOARDING_EXCLUDED_URLS = {
    AuthURLNames.UPLOAD_PROFILE_PICTURE,
}


class OnboardingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.static_url = settings.STATIC_URL.rstrip("/")
        self.media_url = settings.MEDIA_URL.rstrip("/")

    def __call__(self, request):
        
        # Skip static & media files
        path = request.path_info
        if path.startswith(self.static_url) or path.startswith(self.media_url):
            return self.get_response(request)
        
        user = request.user

        if not user.is_authenticated:
            return self.get_response(request)
        
        resolver = resolve(request.path_info)
        if resolver.url_name in ONBOARDING_EXCLUDED_URLS:
            return self.get_response(request)

        manager = resolve_onboarding_manager(user)
        if not manager or manager.is_complete():
            return self.get_response(request)
        
        if resolver.app_name not in ONBOARDING_NAMESPACES:
            return redirect(manager.next_step_url())

        return self.get_response(request)
