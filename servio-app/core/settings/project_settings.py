# project related settings

from core.url_names import AuthURLNames


# custom user model
AUTH_USER_MODEL = "accounts.AuthUser"

LOGOUT_REDIRECT_URL = LOGIN_URL = AuthURLNames.LOGIN
LOGIN_REDIRECT_URL = AuthURLNames.ACCOUNT_DASHBOARD

LOCAL_APPS = [
    "accounts.apps.AccountsConfig",
]

LOCAL_MIDDLEWARES = []

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
