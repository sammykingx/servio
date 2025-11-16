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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    }
}

