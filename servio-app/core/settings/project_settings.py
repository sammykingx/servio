# project related settings

from core.url_names import AuthURLNames


# custom user model
AUTH_USER_MODEL = "accounts.AuthUser"

LOGOUT_REDIRECT_URL = LOGIN_URL = AuthURLNames.LOGIN
LOGIN_REDIRECT_URL = AuthURLNames.ACCOUNT_DASHBOARD

LOCAL_APPS = [
    "accounts.apps.AccountsConfig",
    "notifications.apps.NotificationsConfig",
    "business_accounts.apps.BusinessAccountsConfig",
    "business_services.apps.BusinessServicesConfig",
    "collaboration.apps.CollaborationConfig",
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
