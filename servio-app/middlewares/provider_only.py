from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.conf import settings
from accounts.models.profile import UserRole
from core.url_names import AuthURLNames


class ProviderOnlyMiddleware:
    """
    Restrict all /business/* routes to PROVIDER users only
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/business/"):
            user = request.user

            if not user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            # Logged in but not a provider
            if user.profile.role != UserRole.PROVIDERS:
                messages.info(
                    request,
                    "You must be a provider to access business features.",
                    extra_tags="Access Denied",
                )
                return redirect(reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD))

        return self.get_response(request)

