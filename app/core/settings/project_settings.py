# project related settings

from core.url_names import AuthURLNames
from decouple import config

# custom user model
AUTH_USER_MODEL = "accounts.AuthUser"

LOGIN_URL = AuthURLNames.LOGIN
LOGIN_REDIRECT_URL = AuthURLNames.ACCOUNT_DASHBOARD

LOCAL_APPS = [
    "accounts.apps.AccountsConfig",
    "notifications.apps.NotificationsConfig",
    "business_accounts.apps.BusinessAccountsConfig",
    "business_services.apps.BusinessServicesConfig",
    "collaboration.apps.CollaborationConfig",
    "payments.apps.PaymentsConfig",
]

LOCAL_MIDDLEWARES = [
    "middlewares.onboarding.OnboardingMiddleware",
    "middlewares.provider_only.ProviderOnlyMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "core.backends.auth_backend.MagicLinkBackend",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    }
}

PAYSTACK_SECRET_KEY = config("PAYSTACK_TEST_SECRET_KEY") if config("ENVIRONMENT") == "development" else config("PAYSTACK_LIVE_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_TEST_PUBLIC_KEY") if config("ENVIRONMENT") == "development" else config("PAYSTACK_LIVE_PUBLIC_KEY")
