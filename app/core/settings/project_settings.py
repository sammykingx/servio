# project related settings

from core.url_names import AuthURLNames, PageURLS
from datetime import datetime
from decouple import config

# custom user model
AUTH_USER_MODEL = "accounts.AuthUser"

UNVERIFIED_USER_SESSION_KEY = "unverified_user_session"

LOGIN_URL = AuthURLNames.LOGIN
LOGOUT_REDIRECT_URL = AuthURLNames.LOGIN
LOGIN_REDIRECT_URL = AuthURLNames.ACCOUNT_DASHBOARD

LOCAL_APPS = [
    "accounts.apps.AccountsConfig",
    "business_accounts.apps.BusinessAccountsConfig",
    
    "collaboration.apps.CollaborationConfig",
    "contracts.apps.ContractsConfig",
    "notifications.apps.NotificationsConfig",
    "proposals.apps.ProposalConfig",
    "payments.apps.PaymentsConfig",
]

LOCAL_MIDDLEWARES = [
    "middlewares.pre_launch.PreLaunchMiddleware",
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

LAUNCH_DATE = datetime(2026, 7, 15, 11, 50, 59)

ALLOWED_PRE_LAUNCH_URL_NAMES = {
    PageURLS.WAIT_LIST,
    AuthURLNames.LOGIN,
}

ALLOWED_PATH_PREFIXES = (
    "/static/",
    "/media/",
)